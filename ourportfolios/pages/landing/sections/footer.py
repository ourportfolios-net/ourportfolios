"""Footer section."""

import reflex as rx

from ..components import scroll_reveal


def footer() -> rx.Component:
    """Footer component."""
    return scroll_reveal(
        rx.box(
            rx.hstack(
                rx.text(
                    "ourportfolios",
                    font_size="1.25rem",
                    font_weight="600",
                    letter_spacing="-0.02em",
                    color="rgba(255, 255, 255, 0.8)",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        rx.hstack(
                            rx.icon("github", size=16),
                            "GitHub",
                            spacing="1",
                        ),
                        href="https://github.com/ourportfolios-net/ourportfolios",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                        is_external=True,
                    ),
                    spacing="7",
                    wrap="wrap",
                ),
                justify="between",
                align="start",
                flex_direction=["column", "row"],
                gap="4rem",
                width="100%",
                max_width="80rem",
                margin="0 auto",
                padding_x="2.5rem",
            ),
            border_top="1px solid rgba(255, 255, 255, 0.05)",
            padding_y="5rem",
            padding_x="2.5rem",
        ),
    )
