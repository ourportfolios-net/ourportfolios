"""Navigation bar component."""

import reflex as rx
from .search_bar import search_bar


def navbar() -> rx.Component:
    """Navigation bar with logo and search."""
    bar = rx.box(
        rx.hstack(
            rx.hstack(
                rx.text(
                    "ourportfolios",
                    font_size="1.25rem",
                    font_weight="600",
                    letter_spacing="-0.02em",
                    user_select="none",
                ),
                rx.link(
                    "Home",
                    href="/home",
                    font_size="14px",
                    font_weight="400",
                    color="rgba(255, 255, 255, 0.5)",
                    text_decoration="none",
                    _hover={"color": "white"},
                    transition="color 0.2s",
                ),
                rx.link(
                    "Portfolio",
                    href="/select",
                    font_size="14px",
                    font_weight="400",
                    color="rgba(255, 255, 255, 0.5)",
                    text_decoration="none",
                    _hover={"color": "white"},
                    transition="color 0.2s",
                ),
                rx.link(
                    "Compare",
                    href="/compare",
                    font_size="14px",
                    font_weight="400",
                    color="rgba(255, 255, 255, 0.5)",
                    text_decoration="none",
                    _hover={"color": "white"},
                    transition="color 0.2s",
                ),
                rx.link(
                    "Settings",
                    href="/home",
                    font_size="14px",
                    font_weight="400",
                    color="rgba(255, 255, 255, 0.5)",
                    text_decoration="none",
                    _hover={"color": "white"},
                    transition="color 0.2s",
                ),
                spacing="6",
                align="center",
            ),
            search_bar(),
            align="center",
            justify="between",
            width="100%",
            padding_x="2rem",
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="50",
        padding_y="1rem",
        background="rgba(10, 10, 10, 0.4)",
        backdrop_filter="blur(32px)",
        border_bottom="1px solid rgba(255, 255, 255, 0.05)",
    )

    spacer = rx.box(height="4rem", width="100%")
    return rx.vstack(bar, spacer)
