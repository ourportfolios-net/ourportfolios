"""Industry landing page - industry-specific ticker view."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...utils.session_manager import SessionIsolatedStateMixin


class State(SessionIsolatedStateMixin, rx.State):
    """State for industry analysis page."""

    def on_mount(self):
        """Initialize session when page is mounted."""
        super().on_mount()

    def on_unmount(self):
        """Cleanup when page is unmounted."""
        super().on_unmount()


@rx.page(route="/select/[industry]", on_load=[State.on_mount])
def index():
    return rx.box(
        rx.fragment(
            navbar(),
            rx.box(
                rx.link(
                    rx.hstack(
                        rx.icon("chevron_left", size=22),
                        rx.text("select", margin_top="-0.125rem"),
                        spacing="0",
                    ),
                    href="/select",
                    underline="none",
                ),
                position="fixed",
                justify="center",
                style={"paddingTop": "1em", "paddingLeft": "0.5em"},
                z_index="1",
            ),
            rx.center(
                rx.box(
                    rx.text("Industry landing page content goes here."),
                    width="86vw",
                    max_width="90rem",
                    margin="0 auto",
                ),
                width="100%",
                padding="2em",
                padding_top="5em",
                position="relative",
            ),
            drawer_button(),
        ),
        on_unmount=State.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
