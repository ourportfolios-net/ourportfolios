"""Session management utilities for page isolation and lifecycle control.

Provides synchronous session management with immediate task cancellation on navigation,
preventing cross-page data contamination and ensuring responsive page transitions.
"""

import asyncio
import uuid
from collections.abc import Callable
from functools import wraps

import reflex as rx


class SessionCancelledError(Exception):
    """Raised when an operation is cancelled due to session termination."""


class SessionManager:
    """Manages page session lifecycles to prevent cross-page data contamination."""

    def __init__(self):
        # Track active page sessions per state instance
        self._active_sessions: dict[str, str] = {}  # state_id -> session_id
        # Track cancelled sessions to prevent their operations from completing
        self._cancelled_sessions: set[str] = set()
        # Track running tasks per session for IMMEDIATE cancellation
        self._session_tasks: dict[str, set[asyncio.Task]] = {}

    def start_session(self, state_id: str, force_new: bool = False) -> str:
        """Start a new page session and immediately cancel previous sessions.

        Args:
            state_id: Unique identifier for the state instance
            force_new: If True, cancels sessions from other pages

        Returns:
            Session ID for the new or existing session

        """
        if force_new:
            current_state_class = (
                state_id.rsplit("_", 1)[0] if "_" in state_id else state_id
            )

            sessions_to_cancel = []
            states_to_remove = []

            for sid, session_id in self._active_sessions.items():
                other_state_class = sid.rsplit("_", 1)[0] if "_" in sid else sid

                if other_state_class != current_state_class:
                    sessions_to_cancel.append(session_id)
                    states_to_remove.append(sid)
                    if session_id not in self._cancelled_sessions:
                        self._cancelled_sessions.add(session_id)
                        self._cancel_tasks_immediately(session_id)

            for sid in states_to_remove:
                del self._active_sessions[sid]

            if state_id in self._active_sessions:
                existing_session_id = self._active_sessions[state_id]
                if existing_session_id not in self._cancelled_sessions:
                    return existing_session_id
                del self._active_sessions[state_id]
        elif state_id in self._active_sessions:
            existing_session_id = self._active_sessions[state_id]
            if existing_session_id not in self._cancelled_sessions:
                return existing_session_id

        session_id = str(uuid.uuid4())
        self._active_sessions[state_id] = session_id
        self._session_tasks[session_id] = set()

        return session_id

    def _cancel_tasks_immediately(self, session_id: str):
        """Immediately cancel all tasks for a session.

        Args:
            session_id: The session whose tasks should be cancelled

        """
        if session_id not in self._session_tasks:
            return

        tasks = list(self._session_tasks[session_id])
        active_tasks = [t for t in tasks if not t.done()]

        if active_tasks:
            for task in active_tasks:
                try:
                    task.cancel()
                except Exception as e:
                    print(f"Error: {e}")

        if session_id in self._session_tasks:
            del self._session_tasks[session_id]

    def is_session_active(self, session_id: str) -> bool:
        """Check if a session is still active.

        Args:
            session_id: The session to check

        Returns:
            True if the session is active, False if cancelled

        """
        return session_id not in self._cancelled_sessions

    def register_task(self, session_id: str, task: asyncio.Task):
        """Register a task with a session for immediate cancellation on navigation."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].add(task)
            # Remove task when done
            task.add_done_callback(lambda t: self._remove_task(session_id, t))

    def _remove_task(self, session_id: str, task: asyncio.Task):
        """Remove a completed task from tracking."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].discard(task)

    def get_state_id(self, state) -> str:
        """Get a unique identifier for a state instance."""
        # Cache on state instance if possible
        if hasattr(state, "_cached_state_id") and state._cached_state_id:
            return state._cached_state_id

        # Get client token
        try:
            client_token = state.router.session.client_token
        except (AttributeError, KeyError):
            client_token = None

        # Handle None or empty string
        if not client_token or client_token == "None" or client_token == "null":
            client_token = f"ssr_{uuid.uuid4().hex[:8]}"

        # Use the state's token and full module path
        state_class = state.__class__
        class_identifier = f"{state_class.__module__}.{state_class.__name__}"
        state_id = f"{class_identifier}_{client_token}"

        # Cache it
        try:
            state._cached_state_id = state_id
        except (AttributeError, TypeError):
            pass

        return state_id


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return _session_manager


def session_isolated(func: Callable) -> Callable:
    """Decorator to isolate async event handlers by page session.

    Ensures that background tasks are cancelled when users navigate away,
    preventing cross-page data contamination and resource leaks.

    Args:
        func: The async function to wrap

    Returns:
        Wrapped function with session isolation

    """
    import inspect

    async def _wait_for_session_id(state: rx.State, func_name: str) -> str | None:
        """Helper to wait for session_id to be available.

        Args:
            state: The state instance
            func_name: Name of the function for logging

        Returns:
            session_id if available, None otherwise

        """
        session_id = getattr(state, "_session_id", None)

        if not session_id or session_id == "":
            for attempt in range(6):
                await asyncio.sleep(0.05)
                session_id = getattr(state, "_session_id", None)
                if session_id and session_id != "":
                    return session_id

            print(
                f"Warning: session_id not available for {func_name}, skipping execution",
            )
            return None

        return session_id

    # Check if the original function is a generator function
    if inspect.isasyncgenfunction(func):

        @wraps(func)
        async def wrapper(self: rx.State, *args, **kwargs):
            session_id = await _wait_for_session_id(self, func.__name__)
            if not session_id:
                return

            manager = get_session_manager()

            if not manager.is_session_active(session_id) or not is_client_connected(
                self,
            ):
                return

            current_task = asyncio.current_task()
            if current_task:
                manager.register_task(session_id, current_task)

            try:
                async for item in func(self, *args, **kwargs):
                    if not manager.is_session_active(session_id):
                        return
                    if not is_client_connected(self):
                        return
                    yield item
            except asyncio.CancelledError:
                return
    else:

        @wraps(func)
        async def wrapper(self: rx.State, *args, **kwargs):
            session_id = await _wait_for_session_id(self, func.__name__)
            if not session_id:
                return None

            manager = get_session_manager()

            if not manager.is_session_active(session_id) or not is_client_connected(
                self,
            ):
                return None

            current_task = asyncio.current_task()
            if current_task:
                manager.register_task(session_id, current_task)

            try:
                result = await func(self, *args, **kwargs)

                if not manager.is_session_active(session_id):
                    return None
                if not is_client_connected(self):
                    return None

                return result
            except asyncio.CancelledError:
                return None

    return wrapper


def check_session_active(state) -> bool:
    """Helper to check if current state's session is still active."""
    session_id = getattr(state, "_session_id", None)
    if session_id is None:
        return True

    manager = get_session_manager()
    return manager.is_session_active(session_id)


def is_client_connected(state: rx.State) -> bool:
    """Return True if the state's client token is still bound to a websocket."""
    try:
        token = state.router.session.client_token
    except (AttributeError, KeyError):
        return False

    if not token or token in {"None", "null"}:
        return False

    try:
        from reflex.utils.prerequisites import get_app

        app = get_app().app
        namespace = getattr(app, "event_namespace", None)

        # During startup/tests event namespace may not be initialized yet.
        if namespace is None:
            return True

        token_manager = getattr(namespace, "_token_manager", None)
        token_to_socket = getattr(token_manager, "token_to_socket", None)
        if token_to_socket is not None:
            return token in token_to_socket

        # Compatibility fallback for older/newer APIs.
        token_to_sid = getattr(namespace, "token_to_sid", None)
        if token_to_sid is not None:
            return token in token_to_sid
    except Exception:
        # Do not fail hard if internals change.
        return True

    return True


def is_state_live(state: rx.State) -> bool:
    """Return True when both session and websocket client are still active."""
    return check_session_active(state) and is_client_connected(state)


class SessionIsolatedStateMixin:
    """Mixin to add session isolation to Reflex State classes.

    Provides synchronous session lifecycle management with immediate
    task cancellation on navigation for responsive page transitions.

    Usage:
        class MyState(SessionIsolatedStateMixin, rx.State):
            def on_mount(self):
                super().on_mount()
                # Optional: trigger background data loading

            def on_unmount(self):
                super().on_unmount()
    """

    _session_id: str = ""
    _is_mounted: bool = False
    _cached_state_id: str | None = None

    def on_mount(self) -> object | None:
        """Initialize page session when mounted.

        Creates a new session and cancels tasks from other pages synchronously.
        """
        manager = get_session_manager()
        state_id = manager.get_state_id(self)

        self._session_id = manager.start_session(state_id, force_new=True)
        self._is_mounted = True

    def on_unmount(self) -> object | None:
        """Cleanup page session when unmounted.

        Cancels all running tasks synchronously for instant navigation.
        """
        self._is_mounted = False

        if hasattr(self, "_session_id") and self._session_id:
            manager = get_session_manager()
            session_id = self._session_id

            if session_id not in manager._cancelled_sessions:
                manager._cancelled_sessions.add(session_id)

            manager._cancel_tasks_immediately(session_id)

            state_id = manager.get_state_id(self)
            if state_id in manager._active_sessions:
                if manager._active_sessions[state_id] == session_id:
                    del manager._active_sessions[state_id]

            if len(manager._cancelled_sessions) > 100:
                recent_cancelled = list(manager._cancelled_sessions)[-50:]
                manager._cancelled_sessions = set(recent_cancelled)

    def is_mounted(self) -> bool:
        """Check if page is currently mounted."""
        return self._is_mounted and check_session_active(self)
