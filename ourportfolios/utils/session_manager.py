"""Session management utilities for page isolation and lifecycle control.

This module provides decorators and utilities to isolate page sessions,
preventing race conditions and errors when users navigate between pages
while async operations are still running.
"""

import asyncio
import uuid
from functools import wraps
from collections.abc import Callable
import reflex as rx


class SessionCancelledError(Exception):
    """Raised when an operation is cancelled due to session termination."""

    pass


class SessionManager:
    """Manages page session lifecycles to prevent cross-page data contamination."""

    def __init__(self):
        # Track active page sessions per state instance
        self._active_sessions: dict[str, str] = {}  # state_id -> session_id
        # Track cancelled sessions to prevent their operations from completing
        self._cancelled_sessions: set[str] = set()
        # Track running tasks per session for cleanup
        self._session_tasks: dict[str, set[asyncio.Task]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    def cancel_all_sessions(self):
        """Immediately cancel all active sessions. Called on any navigation."""
        print("🛑 SESSION: Cancelling ALL sessions due to navigation")

        # Mark all as cancelled immediately
        for session_id in self._active_sessions.values():
            self._cancelled_sessions.add(session_id)

        # Clear active sessions
        sessions_to_cancel = list(self._active_sessions.values())
        self._active_sessions.clear()

        # Schedule async cancellation
        for session_id in sessions_to_cancel:
            asyncio.create_task(self.cancel_session(session_id))

    def start_session(self, state_id: str, force_new: bool = False) -> str:
        """Start a new page session and cancel any previous session for this state.

        MUST be synchronous to ensure _session_id is set immediately in on_mount.

        Args:
            state_id: Unique identifier for the state instance
            force_new: If True, always create new session and cancel sessions from OTHER pages.
        """
        # When forcing new, cancel sessions from OTHER state classes (other pages)
        if force_new:
            # Extract the state class name from state_id (format: ClassName_token)
            current_state_class = (
                state_id.rsplit("_", 1)[0] if "_" in state_id else state_id
            )

            # Find sessions from different state classes to cancel
            sessions_to_cancel = []
            states_to_remove = []

            for sid, session_id in self._active_sessions.items():
                # Extract state class from this state_id
                other_state_class = sid.rsplit("_", 1)[0] if "_" in sid else sid

                # Only cancel if it's a different page (different state class)
                if other_state_class != current_state_class:
                    sessions_to_cancel.append(session_id)
                    states_to_remove.append(sid)
                    if session_id not in self._cancelled_sessions:
                        print(
                            f"🔄 SESSION: Cancelling session {session_id[:8]} from {other_state_class} (page navigation)"
                        )
                        # Mark as cancelled immediately to prevent new operations
                        self._cancelled_sessions.add(session_id)

            # Remove those state entries
            for sid in states_to_remove:
                del self._active_sessions[sid]

            # Schedule task cancellation asynchronously (don't block)
            if sessions_to_cancel:
                for session_id in sessions_to_cancel:
                    asyncio.create_task(self.cancel_session(session_id))

            # For THIS state, check if we already have an active session
            if state_id in self._active_sessions:
                existing_session_id = self._active_sessions[state_id]
                # Reuse if still active (handles multiple on_mount calls)
                if existing_session_id not in self._cancelled_sessions:
                    print(
                        f"♻️  SESSION: Reusing existing session {existing_session_id[:8]} for {current_state_class}"
                    )
                    return existing_session_id
                # If cancelled, remove it so we can create new
                del self._active_sessions[state_id]
        else:
            # Just check if we can reuse existing session for same state
            if state_id in self._active_sessions:
                existing_session_id = self._active_sessions[state_id]
                if existing_session_id not in self._cancelled_sessions:
                    print(
                        f"♻️  SESSION: Reusing existing session {existing_session_id[:8]} for {state_id}"
                    )
                    return existing_session_id

        # Create new session
        session_id = str(uuid.uuid4())
        self._active_sessions[state_id] = session_id
        self._session_tasks[session_id] = set()

        print(f"✅ SESSION: Started new session {session_id[:8]} for {state_id}")
        return session_id

    async def cancel_session(self, session_id: str):
        """Cancel a session and all its running tasks."""
        if session_id in self._cancelled_sessions:
            return  # Already cancelled

        self._cancelled_sessions.add(session_id)

        # Cancel all tasks for this session
        if session_id in self._session_tasks:
            tasks = list(self._session_tasks[session_id])
            active_tasks = [t for t in tasks if not t.done()]

            if active_tasks:
                print(
                    f"❌ SESSION: Cancelling {len(active_tasks)} running tasks for session {session_id[:8]}"
                )

                # Cancel all tasks
                for task in active_tasks:
                    task.cancel()

                # Wait for cancellation with timeout
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*active_tasks, return_exceptions=True),
                        timeout=5.0,
                    )
                except asyncio.TimeoutError:
                    print(
                        f"⚠️  SESSION: Some tasks did not cancel within timeout for session {session_id[:8]}"
                    )

            del self._session_tasks[session_id]

    def is_session_active(self, session_id: str) -> bool:
        """Check if a session is still active (not cancelled)."""
        return session_id not in self._cancelled_sessions

    def register_task(self, session_id: str, task: asyncio.Task):
        """Register a task with a session for cleanup."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].add(task)
            print(
                f"📝 SESSION: Registered task {task.get_name()} for session {session_id[:8]} (total: {len(self._session_tasks[session_id])} tasks)"
            )
            # Remove task when done
            task.add_done_callback(lambda t: self._remove_task(session_id, t))

    def _remove_task(self, session_id: str, task: asyncio.Task):
        """Remove a completed task from tracking."""
        if session_id in self._session_tasks:
            self._session_tasks[session_id].discard(task)

    async def cleanup_session(self, session_id: str):
        """Cleanup a session after it's finished."""
        async with self._lock:
            self._cancelled_sessions.discard(session_id)
            if session_id in self._session_tasks:
                del self._session_tasks[session_id]
            # Remove from active sessions if present
            state_ids_to_remove = [
                state_id
                for state_id, sid in self._active_sessions.items()
                if sid == session_id
            ]
            for state_id in state_ids_to_remove:
                del self._active_sessions[state_id]

    def get_state_id(self, state) -> str:
        """Get a unique identifier for a state instance."""
        # Cache on state instance if possible
        if hasattr(state, "_cached_state_id") and state._cached_state_id:
            return state._cached_state_id

        # Get client token, fallback to a generated ID if None (during SSR)
        try:
            client_token = state.router.session.client_token
        except (AttributeError, KeyError):
            client_token = None

        # Handle None or empty string
        if not client_token or client_token == "None" or client_token == "null":
            # During server-side rendering or before client connects, generate a unique token
            client_token = f"ssr_{uuid.uuid4().hex[:8]}"

        # Use the state's token and full module path to identify unique state instances
        # This ensures different pages with same class name get different sessions
        state_class = state.__class__
        class_identifier = f"{state_class.__module__}.{state_class.__name__}"
        state_id = f"{class_identifier}_{client_token}"

        # Cache it
        try:
            state._cached_state_id = state_id
        except (AttributeError, TypeError):
            pass  # State might not allow attribute assignment

        return state_id

    async def _cleanup_old_cancelled_sessions(self):
        """Periodically clean up cancelled sessions to prevent memory leak."""
        async with self._lock:
            # Keep only sessions that still have active tasks
            active_session_ids = set(self._session_tasks.keys())
            sessions_to_keep = active_session_ids | set(self._active_sessions.values())

            # Remove cancelled sessions that are no longer referenced
            self._cancelled_sessions = self._cancelled_sessions & sessions_to_keep

            print(
                f"🧹 SESSION: Cleaned up old cancelled sessions. Active: {len(sessions_to_keep)}"
            )


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return _session_manager


def session_isolated(func: Callable) -> Callable:
    """Decorator to isolate async event handlers by page session.

    This decorator:
    1. Checks if the current session is still active before executing
    2. Periodically checks during execution if session is still active
    3. Cancels operation if user has navigated away

    Usage:
        @rx.event
        @session_isolated
        async def load_data(self):
            # This will auto-cancel if user navigates away
            await fetch_from_api()
    """

    @wraps(func)
    async def wrapper(self: rx.State, *args, **kwargs):
        # Get current session ID for this state
        session_id = getattr(self, "_session_id", None)

        # If no session ID, wait briefly for on_mount to create one
        if not session_id or session_id == "":
            # Wait up to 2 seconds for session to be created by on_mount
            for _ in range(20):  # 20 * 0.1s = 2 seconds max
                await asyncio.sleep(0.1)
                session_id = getattr(self, "_session_id", None)
                if session_id and session_id != "":
                    break
            else:
                # Still no session after waiting
                print(
                    f"⚠️  SESSION: Blocked execution of {func.__name__} (no active session - page not mounted yet)"
                )
                return  # Silently skip execution

        manager = get_session_manager()

        # Check if session is still active
        if not manager.is_session_active(session_id):
            print(
                f"⚠️  SESSION: Blocked execution of {func.__name__} (session {session_id[:8]} already cancelled)"
            )
            return  # Silently skip - don't crash the app

        try:
            print(f"▶️  SESSION: Executing {func.__name__} in session {session_id[:8]}")
            # Execute the function
            result = await func(self, *args, **kwargs)

            # Check again after execution
            if not manager.is_session_active(session_id):
                print(
                    f"🛑 SESSION: Discarding result from {func.__name__} (session {session_id[:8]} cancelled during execution)"
                )
                return  # Silently discard result - don't crash

            print(f"✔️  SESSION: Completed {func.__name__} in session {session_id[:8]}")

            # Cleanup cancelled sessions list periodically to prevent memory leak
            if len(manager._cancelled_sessions) > 100:
                await manager._cleanup_old_cancelled_sessions()

            return result
        except (asyncio.CancelledError, SessionCancelledError):
            # Task was cancelled, clean exit
            print(
                f"🚫 SESSION: Task {func.__name__} cancelled (session {session_id[:8]})"
            )
            raise SessionCancelledError(f"Session {session_id[:8]} was cancelled")

    return wrapper


def check_session_active(state) -> bool:
    """Helper to check if current state's session is still active.

    Usage inside event handlers:
        async def load_data(self):
            data = await fetch_data()
            if not check_session_active(self):
                return  # Stop processing
            self.data = data
    """
    session_id = getattr(state, "_session_id", None)
    if session_id is None:
        return True  # No session isolation, assume active

    manager = get_session_manager()
    return manager.is_session_active(session_id)


class SessionIsolatedStateMixin:
    """Mixin to add session isolation to Reflex State classes.

    Usage:
        class MyPageState(SessionIsolatedStateMixin, rx.State):
            # ... your state vars ...

            @rx.event
            async def on_mount(self):
                await super().on_mount()  # Initialize session
                await self.load_data()

            @rx.event
            async def on_unmount(self):
                await super().on_unmount()  # Cleanup session

            @rx.event
            @session_isolated
            async def load_data(self):
                # Will auto-cancel if user navigates away
                pass
    """

    # Declare state variables
    _session_id: str = ""
    _is_mounted: bool = False
    _cached_state_id: str | None = None

    async def on_mount(self):
        """Initialize page session when mounted.

        Must be async for Reflex on_load compatibility.
        Cancels all sessions and creates this page's session IMMEDIATELY.
        """
        manager = get_session_manager()

        # Cancel ALL sessions immediately (sync operation - no await)
        print(f"🎯 ON_MOUNT: Cancelling all sessions and creating new one")
        manager.cancel_all_sessions()

        # Create this page's session immediately (sync operation)
        state_id = manager.get_state_id(self)
        self._session_id = manager.start_session(state_id, force_new=False)
        self._is_mounted = True
        print(
            f"🔧 SESSION: on_mount completed, _session_id set to {self._session_id[:8]}"
        )

    async def on_unmount(self):
        """Cleanup page session when unmounted."""
        self._is_mounted = False
        if hasattr(self, "_session_id") and self._session_id:
            manager = get_session_manager()
            session_id = self._session_id
            await manager.cancel_session(session_id)
            # Schedule cleanup after brief delay
            asyncio.create_task(self._delayed_cleanup(session_id))

    async def _delayed_cleanup(self, session_id: str):
        """Cleanup session after a delay to ensure all operations complete."""
        await asyncio.sleep(1.0)  # Wait for any pending operations
        manager = get_session_manager()
        await manager.cleanup_session(session_id)

    def is_mounted(self) -> bool:
        """Check if page is currently mounted."""
        return self._is_mounted and check_session_active(self)


async def create_background_task(state, coro) -> asyncio.Task:
    """Create a background task that's tracked by the session manager.

    The task will be automatically cancelled if the session ends.

    Usage:
        task = await create_background_task(self, self._fetch_data())
        await task
    """
    session_id = getattr(state, "_session_id", None)
    task = asyncio.create_task(coro)

    if session_id:
        manager = get_session_manager()
        # Ensure session still exists before registering
        if manager.is_session_active(session_id):
            manager.register_task(session_id, task)
        else:
            # Session already cancelled, cancel this task immediately
            task.cancel()
            raise SessionCancelledError(
                f"Cannot create task - session already cancelled"
            )

    return task
