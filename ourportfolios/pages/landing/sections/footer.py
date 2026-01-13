"""Footer component."""

import reflex as rx

from ..components import scroll_reveal


def footer() -> rx.Component:
    """Footer component."""
    return scroll_reveal(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "ourportfolios",
                        font_size="1.25rem",
                        font_weight="600",
                        letter_spacing="-0.02em",
                    ),
                    rx.text(
                        "© 2024 ourportfolios. Built for precision.",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.2)",
                    ),
                    spacing="4",
                    align="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        "Privacy",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "Terms",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "Twitter",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "GitHub",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
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
