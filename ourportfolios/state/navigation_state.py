"""Global navigation state that cancels sessions on route changes."""

import reflex as rx

from ourportfolios.utils.session_manager import get_session_manager


class GlobalNavigationState(rx.State):
    """Global state that monitors route changes and cancels sessions."""

    _last_route: str = ""

    def _on_state_update(self) -> None:
        """Handle each state update and check for route changes."""
        try:
            current_route = self.router.page.path
            if self._last_route not in ("", current_route):
                # Cancel all sessions immediately
                manager = get_session_manager()
                cancel_all = getattr(manager, "cancel_all_sessions", None)
                if callable(cancel_all):
                    cancel_all()
            self._last_route = current_route
        except (AttributeError, KeyError):
            pass  # Router not ready yet
