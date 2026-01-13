"""Navigation bar component."""

import reflex as rx
from .search_bar import search_bar


def navbar() -> rx.Component:
    """Fixed navigation bar with logo and search bar."""
    return rx.box(
        rx.hstack(
            # Logo
            rx.text(
                "ourportfolios",
                size="4",
                weight="bold",
            ),
            rx.spacer(),
            # Search bar
            search_bar(),
            rx.spacer(),
            align="center",
            width="100%",
            max_width="80rem",
            px="4",
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="50",
        py="4",
        background="rgba(17, 17, 19, 0.7)",
        backdrop_filter="blur(32px)",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
    )
