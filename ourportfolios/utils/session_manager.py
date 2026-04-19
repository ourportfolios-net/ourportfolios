"""Manage state sessions and task isolation for Reflex pages."""

from __future__ import annotations

import asyncio
import inspect
import logging
import uuid
from functools import wraps
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable
    from types import ModuleType

try:
    from reflex.utils.prerequisites import get_app as _get_app

    get_app: Callable[[bool], ModuleType] | None = _get_app
except ImportError:  # pragma: no cover
    get_app: Callable[[bool], ModuleType] | None = None

LOGGER = logging.getLogger(__name__)
SESSION_WAIT_ATTEMPTS = 6
SESSION_WAIT_DELAY_SECONDS = 0.05
MISSING_TOKEN_VALUES = {"none", "null"}


class SessionCancelledError(Exception):
    """Raise when an operation is cancelled due to session termination."""


class SessionManager:
    """Manage page sessions to prevent cross-page data contamination."""

    CANCELLED_SESSION_LIMIT = 100
    CANCELLED_SESSION_KEEP = 50

    def __init__(self) -> None:
        self._active_sessions: dict[str, str] = {}
        self._cancelled_sessions: set[str] = set()
        self._session_tasks: dict[str, set[asyncio.Task[object]]] = {}
        self._state_cache: dict[int, str] = {}

    def start_session(self, state_id: str, *, force_new: bool = False) -> str:
        """Start a session and optionally cancel sessions from other pages."""
        if force_new:
            self._cancel_other_page_sessions(state_id)
            existing_session = self._active_sessions.get(state_id)
            if existing_session and self.is_session_active(existing_session):
                return existing_session
            self._active_sessions.pop(state_id, None)
        else:
            existing_session = self._active_sessions.get(state_id)
            if existing_session and self.is_session_active(existing_session):
                return existing_session

        session_id = str(uuid.uuid4())
        self._active_sessions[state_id] = session_id
        self._session_tasks[session_id] = set()
        return session_id

    def _cancel_other_page_sessions(self, state_id: str) -> None:
        current_state_class = (
            state_id.rsplit("_", 1)[0] if "_" in state_id else state_id
        )
        states_to_remove: list[str] = []

        for other_state_id, session_id in self._active_sessions.items():
            other_state_class = (
                other_state_id.rsplit("_", 1)[0]
                if "_" in other_state_id
                else other_state_id
            )
            if other_state_class == current_state_class:
                continue
            self.cancel_session(session_id)
            states_to_remove.append(other_state_id)

        for other_state_id in states_to_remove:
            self._active_sessions.pop(other_state_id, None)

    def _cancel_tasks_immediately(self, session_id: str) -> None:
        """Cancel all tasks currently tracked for a session."""
        tasks = list(self._session_tasks.get(session_id, set()))
        for task in tasks:
            if not task.done():
                task.cancel()
        self._session_tasks.pop(session_id, None)

    def is_session_active(self, session_id: str) -> bool:
        """Return whether a session has not been cancelled."""
        return session_id not in self._cancelled_sessions

    def register_task(self, session_id: str, task: asyncio.Task[object]) -> None:
        """Register a task for cancellation when its session is ended."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].add(task)
            task.add_done_callback(
                lambda done_task: self._remove_task(session_id, done_task),
            )

    def _remove_task(self, session_id: str, task: asyncio.Task[object]) -> None:
        """Remove a completed task from session tracking."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].discard(task)

    def get_state_id(self, state: object) -> str:
        """Return a stable identifier for a state instance."""
        state_key = id(state)
        cached_state_id = self._state_cache.get(state_key)
        if cached_state_id:
            return cached_state_id

        client_token = _get_client_token(state)
        if _is_missing_client_token(client_token):
            client_token = _make_server_session_token()

        state_class = state.__class__
        class_identifier = f"{state_class.__module__}.{state_class.__name__}"
        state_id = f"{class_identifier}_{client_token}"
        self._state_cache[state_key] = state_id
        return state_id

    def cancel_session(self, session_id: str) -> None:
        """Cancel a session and all its tracked tasks."""
        self._cancelled_sessions.add(session_id)
        self._cancel_tasks_immediately(session_id)

    def clear_state_session(self, state_id: str, expected_session_id: str) -> None:
        """Remove active mapping when it still points to the expected session."""
        if self._active_sessions.get(state_id) == expected_session_id:
            self._active_sessions.pop(state_id, None)

    def prune_cancelled_sessions(self) -> None:
        """Keep cancelled-session tracking bounded to recent entries."""
        if len(self._cancelled_sessions) <= self.CANCELLED_SESSION_LIMIT:
            return
        recent_cancelled = list(self._cancelled_sessions)[
            -self.CANCELLED_SESSION_KEEP :
        ]
        self._cancelled_sessions = set(recent_cancelled)


def _make_server_session_token() -> str:
    return f"ssr_{uuid.uuid4().hex[:8]}"


def _is_missing_client_token(token: str | None) -> bool:
    if token is None:
        return True
    stripped = token.strip()
    if stripped == "":
        return True
    return stripped.lower() in MISSING_TOKEN_VALUES


def _get_client_token(state: object) -> str | None:
    router = getattr(state, "router", None)
    if router is None:
        return None
    session = getattr(router, "session", None)
    if session is None:
        return None
    token = getattr(session, "client_token", None)
    return None if token is None else str(token)


def _is_runtime_client_connected(token: str) -> bool:
    if get_app is None:
        return True

    try:
        dry_run = False
        app_module = get_app(dry_run)
    except (AttributeError, KeyError, RuntimeError, TypeError):
        return True

    app = getattr(app_module, "app", None)
    namespace = getattr(app, "event_namespace", None) if app is not None else None
    if namespace is None:
        return True

    token_manager = getattr(namespace, "_token_manager", None)
    token_to_socket = getattr(token_manager, "token_to_socket", None)
    if token_to_socket is not None:
        return token in token_to_socket

    token_to_sid = getattr(namespace, "token_to_sid", None)
    if token_to_sid is None:
        return True
    return token in token_to_sid


def _state_is_session_valid(
    state: object,
    manager: SessionManager,
    session_id: str,
) -> bool:
    return manager.is_session_active(session_id) and is_client_connected(state)


async def _wait_for_session_id(state: object, func_name: str) -> str | None:
    """Wait briefly for a state session id to become available."""
    session_id = getattr(state, "_session_id", None)
    if isinstance(session_id, str) and session_id:
        return session_id

    for _attempt in range(SESSION_WAIT_ATTEMPTS):
        await asyncio.sleep(SESSION_WAIT_DELAY_SECONDS)
        candidate = getattr(state, "_session_id", None)
        if isinstance(candidate, str) and candidate:
            return candidate

    LOGGER.warning("session_id not available for %s; skipping execution", func_name)
    return None


async def _iterate_isolated(
    func: Callable[..., object],
    state: object,
    call_args: tuple[tuple[object, ...], dict[str, object]],
    call_context: tuple[SessionManager, str],
) -> AsyncIterator[object]:
    args, kwargs = call_args
    manager, session_id = call_context

    try:
        iterator = cast("AsyncIterator[object]", func(state, *args, **kwargs))
        async for item in iterator:
            if not _state_is_session_valid(state, manager, session_id):
                return
            yield item
    except asyncio.CancelledError:
        return


async def _await_isolated(
    func: Callable[..., object],
    state: object,
    call_args: tuple[tuple[object, ...], dict[str, object]],
    call_context: tuple[SessionManager, str],
) -> object | None:
    args, kwargs = call_args
    manager, session_id = call_context

    try:
        awaitable = cast("Awaitable[object]", func(state, *args, **kwargs))
        result = await awaitable
    except asyncio.CancelledError:
        return None

    if not _state_is_session_valid(state, manager, session_id):
        return None
    return result


_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Return the process-wide session manager instance."""
    return _session_manager


def _make_asyncgen_wrapper(
    func: Callable[..., object],
) -> Callable[..., AsyncIterator[object]]:
    @wraps(func)
    async def asyncgen_wrapper(
        self: object,
        *args: object,
        **kwargs: object,
    ) -> AsyncIterator[object]:
        func_name = getattr(func, "__name__", "session_handler")
        session_id = await _wait_for_session_id(self, func_name)
        if not session_id:
            return

        manager = get_session_manager()
        if not _state_is_session_valid(self, manager, session_id):
            return

        current_task = asyncio.current_task()
        if current_task is not None:
            manager.register_task(session_id, current_task)

        call_args = (args, kwargs)
        call_context = (manager, session_id)
        async for item in _iterate_isolated(func, self, call_args, call_context):
            yield item

    return asyncgen_wrapper


def _make_async_wrapper(
    func: Callable[..., object],
) -> Callable[..., Awaitable[object | None]]:
    @wraps(func)
    async def async_wrapper(
        self: object,
        *args: object,
        **kwargs: object,
    ) -> object | None:
        func_name = getattr(func, "__name__", "session_handler")
        session_id = await _wait_for_session_id(self, func_name)
        if not session_id:
            return None

        manager = get_session_manager()
        if not _state_is_session_valid(self, manager, session_id):
            return None

        current_task = asyncio.current_task()
        if current_task is not None:
            manager.register_task(session_id, current_task)

        call_args = (args, kwargs)
        call_context = (manager, session_id)
        return await _await_isolated(func, self, call_args, call_context)

    return async_wrapper


def session_isolated(func: Callable[..., object]) -> Callable[..., object]:
    """Wrap an async handler so it respects the active page session."""
    if inspect.isasyncgenfunction(func):
        return cast("Callable[..., object]", _make_asyncgen_wrapper(func))
    return cast("Callable[..., object]", _make_async_wrapper(func))


def check_session_active(state: object) -> bool:
    """Return whether the state's session is still active."""
    session_id = getattr(state, "_session_id", None)
    if session_id is None:
        return True
    manager = get_session_manager()
    return manager.is_session_active(session_id)


def is_client_connected(state: object) -> bool:
    """Return whether the state's client token is still websocket-bound."""
    token = _get_client_token(state)
    if _is_missing_client_token(token):
        return False
    return _is_runtime_client_connected(token or "")


def is_state_live(state: object) -> bool:
    """Return whether both session and websocket client are active."""
    return check_session_active(state) and is_client_connected(state)


class SessionIsolatedStateMixin:
    """Add session isolation lifecycle hooks to a Reflex state class."""

    _session_id: str = ""
    _is_mounted: bool = False
    _cached_state_id: str | None = None

    def on_mount(self) -> object | None:
        """Initialize page session and cancel stale sessions from other pages."""
        manager = get_session_manager()
        state_id = manager.get_state_id(self)
        self._session_id = manager.start_session(state_id, force_new=True)
        self._is_mounted = True
        return None

    def on_unmount(self) -> object | None:
        """Cancel running tasks and clean up the active session mapping."""
        self._is_mounted = False
        if not self._session_id:
            return None

        manager = get_session_manager()
        session_id = self._session_id
        manager.cancel_session(session_id)

        state_id = manager.get_state_id(self)
        manager.clear_state_session(state_id, session_id)
        manager.prune_cancelled_sessions()
        return None

    def is_mounted(self) -> bool:
        """Return whether the page is mounted and its session is active."""
        return self._is_mounted and check_session_active(self)
