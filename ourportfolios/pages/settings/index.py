"""Place at: ourportfolios/pages/settings/index.py"""

import reflex as rx

from ourportfolios.components.auth_guard import page_guard
from ourportfolios.components.navbar import navbar
from ourportfolios.pages.settings.components import settings_layout
from ourportfolios.pages.settings.state import SettingsState
from ourportfolios.state.auth_state import AuthState
from ourportfolios.styles import PAGE_BG, TEXT_MUTED, TEXT_PRIMARY
from ourportfolios.ui.layout import app_shell


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
            settings_layout(),
            max_width="56rem",
            width="100%",
            margin="0 auto",
            padding_x="2rem",
            padding_y="2.5rem",
        ),
    )


@rx.page(
    route="/settings",
    on_load=[AuthState.require_auth, SettingsState.load_settings],
)
def index() -> rx.Component:
    return app_shell(page_guard(_page_body(), bg=PAGE_BG))
