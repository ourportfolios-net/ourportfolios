"""Landing page - main entry point to the application."""

import reflex as rx

from ..landing.components.plasma import plasma
from ..landing.components.shiny_text import shiny_text
from ...utils.session_manager import SessionIsolatedStateMixin

cards = [
    {"title": "Recommend", "details": "Card 1 details", "link": "/recommend"},
    {"title": "Select", "details": "Card 2 details", "link": "/select"},
    {"title": "Analyze", "details": "Card 3 details", "link": "/analyze"},
    {"title": "Simulate", "details": "Card 4 details", "link": "/simulate"},
]


class State(SessionIsolatedStateMixin, rx.State):
    show_cards: bool = False
    data: list[dict] = []

    def on_mount(self):
        """Initialize session when page is mounted."""
        super().on_mount()

    def on_unmount(self):
        """Cleanup when page is unmounted."""
        super().on_unmount()


@rx.page(route="/", on_load=[State.on_mount])
def index() -> rx.Component:
    return rx.box(
        # Plasma background layer - scrolls with content
        rx.box(
            plasma(
                color="#ECD9FA",
                speed=1,
                direction="forward",
                scale=2,
                opacity=0.1,
                mouse_interactive=True,
            ),
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="-1",
            pointer_events="auto",  # Ensure background can receive events
        ),
        rx.vstack(
            rx.center(
                rx.vstack(
                    shiny_text(
                        text="ourportfolios",
                        speed=1,
                        color="#c0c0c0",
                        shine_color="#ffffff",
                        spread=80,
                        direction="left",
                        yoyo=False,
                        font_size="5rem",
                        font_weight="heavy",
                        delay=8,
                    ),
                    rx.text("Build your portfolios. We'll build ours", size="4"),
                    spacing="1",
                    align="center",
                    pointer_events="auto",
                ),
                height="calc(100vh - 64px)",
                width="100%",
                justify="center",
                align="center",
                pointer_events="none",
            ),
            spacing="0",
            align="center",
            width="100%",
            position="relative",
            z_index="10",
            pointer_events="none",
        ),
        on_unmount=State.on_unmount,
        position="relative",  # Add this
        pointer_events="none",  # Add this to root box
        width="100%",
        min_height="100vh",
    )
