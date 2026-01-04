"""Global navigation state that cancels sessions on route changes."""

import reflex as rx
from ..utils.session_manager import get_session_manager


class GlobalNavigationState(rx.State):
    """Global state that monitors route changes and cancels sessions."""

    _last_route: str = ""

    def _on_state_update(self):
        """Called on every state update. Check for route changes."""
        try:
            current_route = self.router.page.path
            if current_route != self._last_route and self._last_route != "":
                # Cancel all sessions immediately
                manager = get_session_manager()
                manager.cancel_all_sessions()
            self._last_route = current_route
        except (AttributeError, KeyError):
            pass  # Router not ready yet
