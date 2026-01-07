"""Landing page - main entry point to the application."""

import reflex as rx

from ...components.navbar import navbar
from ...components.cards import portfolio_card
from ...components.graph import mini_price_graph
from ...components.loading import loading_screen
from ...components.plasma import plasma
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
                opacity=0.15,
                mouse_interactive=True,  # TODO: Make this work
            ),
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="0",
        ),
        # Content layer
        rx.box(
            loading_screen(),
            navbar(
                rx.foreach(
                    State.data,
                    lambda data: mini_price_graph(
                        label=data["label"],
                        data=data["data"],
                        diff=data["percent_diff"],
                    ),
                ),
            ),
            rx.vstack(
                rx.center(
                    rx.vstack(
                        rx.heading(
                            "OurPortfolios", size="9", font_size="5rem", weight="medium"
                        ),
                        rx.text("Build your portfolios. We'll build ours", size="4"),
                        spacing="5",
                        align="center",
                    ),
                    height="calc(100vh - 64px)",
                    width="100%",
                    justify="center",
                    align="center",
                ),
                rx.center(
                    rx.box(
                        *[
                            portfolio_card(card, idx, len(cards))
                            for idx, card in enumerate(cards)
                        ],
                        width="100vw",
                        height="60vh",
                        min_height="40vh",
                        position="relative",
                        overflow="visible",
                        padding_x="7vw",
                    ),
                    width="100%",
                    height="50vh",
                ),
                spacing="0",
                align="center",
                width="100%",
            ),
            position="relative",
            z_index="1",
            min_height="100vh",
            on_unmount=State.on_unmount,
        ),
        position="relative",
        min_height="100vh",
    )
