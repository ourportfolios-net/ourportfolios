"""Framework recommendation page."""

import reflex as rx

from ourportfolios.components.auth_guard import page_guard
from ourportfolios.pages.framework.page_components import page_body
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.layout import app_shell


@rx.page(
    route="/framework",
    on_load=[AuthState.require_auth, FrameworkState.on_mount],
)
def index() -> rx.Component:
    return rx.box(
        app_shell(page_guard(page_body())),
        on_unmount=FrameworkState.on_unmount,
    )
