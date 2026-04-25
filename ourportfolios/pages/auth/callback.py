import reflex as rx

from ourportfolios.pages.auth.components import session_check_screen
from ourportfolios.state.auth_state import AuthState


@rx.page(route="/auth/callback", on_load=AuthState.handle_oauth_callback)
def callback() -> rx.Component:
    return session_check_screen()
