"""Landing page layout and sections."""

import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.pages.landing.sections import (
    bento_section,
    cta_section,
    footer,
    hero_section,
    showcase_section,
)
from ourportfolios.ui.layout import app_shell
from ourportfolios.utils.session_manager import SessionIsolatedStateMixin


class LandingState(SessionIsolatedStateMixin, rx.State):
    """Landing page state."""

    def on_mount(self):
        super().on_mount()

    def on_unmount(self):
        super().on_unmount()


@rx.page(route="/", on_load=LandingState.on_mount)
def index() -> rx.Component:
    """Render the landing page."""
    return rx.box(
        app_shell(
            navbar(),
            hero_section(),
            rx.box(id="showcase"),
            showcase_section(),
            rx.box(id="features"),
            bento_section(),
            rx.box(id="pricing"),
            cta_section(),
            footer(),
        ),
        on_unmount=LandingState.on_unmount,
    )
