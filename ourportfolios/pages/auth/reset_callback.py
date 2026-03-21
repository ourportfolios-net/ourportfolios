"""Place at: ourportfolios/pages/auth/reset_callback.py"""

import reflex as rx
from ...state.auth_state import AuthState
from .components import session_check_screen


@rx.page(route="/auth/reset-callback", on_load=AuthState.handle_reset_callback)
def reset_callback() -> rx.Component:
    return session_check_screen()
