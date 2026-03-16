"""Place at: ourportfolios/pages/account/index.py"""

import reflex as rx
from ...components.navbar import navbar
from ...components.auth_guard import page_guard
from ...state.auth_state import AuthState
from .state import AccountState
from .components import account_layout
from ...styles import TEXT_PRIMARY, TEXT_MUTED, PAGE_BG


def _page_body() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.text(
                    "Settings",
                    font_size="1.625rem",
                    font_weight="700",
                    color=TEXT_PRIMARY,
                    letter_spacing="-0.025em",
                ),
                rx.text(
                    "Manage your account preferences and security.",
                    size="2",
                    color=TEXT_MUTED,
                ),
                spacing="1",
                align="start",
                margin_bottom="2rem",
            ),
            account_layout(),
            max_width="56rem",
            width="100%",
            margin="0 auto",
            padding_x="2rem",
            padding_y="2.5rem",
        ),
        background=PAGE_BG,
        color="white",
        min_height="100vh",
    )


@rx.page(
    route="/account",
    on_load=[AuthState.require_auth, AccountState.load_account],
)
def index() -> rx.Component:
    return page_guard(_page_body(), bg=PAGE_BG)
