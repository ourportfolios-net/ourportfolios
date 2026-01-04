"""Analyze page - navigation hub for analysis features."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.page_roller import card_roller, card_link
from ...components.loading import loading_screen
from ...utils.session_manager import SessionIsolatedStateMixin


class State(SessionIsolatedStateMixin, rx.State):
    """State for analyze page."""

    def on_mount(self):
        """Initialize session when page is mounted."""
        super().on_mount()

    def on_unmount(self):
        """Cleanup when page is unmounted."""
        super().on_unmount()


def page_selection():
    return rx.box(
        card_roller(
            card_link(
                rx.hstack(
                    rx.icon("chevron_left", size=32),
                    rx.vstack(
                        rx.heading("Select", weight="medium", size="5"),
                        rx.text("caijdo", size="1"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    align="center",
                    justify="center",
                ),
                href="/select",
            ),
            card_link(
                rx.vstack(
                    rx.heading("Analyze", weight="medium", size="7"),
                    rx.text("caijdo", size="3"),
                    align="center",
                    justify="center",
                    height="100%",
                    spacing="1",
                ),
                href="/analyze",
            ),
            card_link(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Simulate", weight="medium", size="5"),
                        rx.text("caijdo", size="1"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    rx.icon("chevron_right", size=32),
                    align="center",
                    justify="center",
                ),
                href="/simulate",
            ),
        ),
        width="100%",
        display="flex",
        justify_content="center",
        align_items="center",
        margin="0",
        padding="0",
    )


def compare_blocks():
    """Two blocks that link to /analyze/compare"""
    return rx.hstack(
        rx.link(
            rx.card(
                rx.vstack(
                    rx.heading("Quant", weight="medium", size="6"),
                    rx.text("Quantify stats etc.", size="2"),
                    align="center",
                    justify="center",
                    height="100%",
                    spacing="2",
                ),
                width="300px",
                height="150px",
                padding="4",
                cursor="pointer",
                _hover={"transform": "scale(1.02)"},
                transition="transform 0.2s ease",
            ),
            href="/analyze/quantify",
        ),
        rx.link(
            rx.card(
                rx.vstack(
                    rx.heading("Compare Stocks", weight="medium", size="6"),
                    rx.text("Side by side analysis", size="2"),
                    align="center",
                    justify="center",
                    height="100%",
                    spacing="2",
                ),
                width="300px",
                height="150px",
                padding="4",
                cursor="pointer",
                _hover={"transform": "scale(1.02)"},
                transition="transform 0.2s ease",
            ),
            href="/analyze/compare",
        ),
        spacing="4",
        width="100%",
        justify="center",
        align="center",
    )


@rx.page(route="/analyze", on_load=[State.on_mount])
def index() -> rx.Component:
    """Main page component"""
    return rx.box(
        rx.vstack(
            loading_screen(),
            navbar(),
            page_selection(),
            compare_blocks(),
            drawer_button(),
            spacing="0",
        ),
        on_unmount=State.on_unmount,
    )
