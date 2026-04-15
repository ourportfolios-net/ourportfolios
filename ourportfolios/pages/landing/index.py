"""Landing page layout and sections."""

import reflex as rx

from .sections import (
    hero_section,
    showcase_section,
    bento_section,
    cta_section,
    footer,
)
from ...ui.layout import app_shell
from ...utils.session_manager import SessionIsolatedStateMixin
from ...components.navbar import navbar


class LandingState(SessionIsolatedStateMixin, rx.State):
    """Landing page state."""

    def on_mount(self):
        super().on_mount()

    def on_unmount(self):
        super().on_unmount()


@rx.page(route="/", on_load=LandingState.on_mount)
def index() -> rx.Component:
    """Render the landing page."""
    return app_shell(
        navbar(),
        hero_section(),
        rx.box(id="showcase"),
        showcase_section(),
        rx.box(id="features"),
        bento_section(),
        rx.box(id="pricing"),
        cta_section(),
        footer(),
        on_unmount=LandingState.on_unmount,
    )
