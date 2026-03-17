import reflex as rx
from ...state.auth_state import AuthState
from .components import session_check_screen


@rx.page(route="/auth/callback", on_load=AuthState.handle_oauth_callback)
def callback() -> rx.Component:
    return session_check_screen()
