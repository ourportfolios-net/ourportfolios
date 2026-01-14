"""Call-to-action section component."""

import reflex as rx

from ..components import scroll_reveal, badge_button


def cta_section() -> rx.Component:
    """Call-to-action section."""
    return scroll_reveal(
        rx.center(
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Ready to build the future?",
                        size="8",
                        font_weight="600",
                        letter_spacing="-0.02em",
                        line_height="1.2",
                        margin_bottom="2rem",
                        text_align="center",
                        color="rgba(255, 255, 255, 0.8)",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                rx.hstack(
                                    rx.text("Start for free"),
                                    rx.icon("chevron-right", size=18),
                                    spacing="2",
                                    align="center",
                                ),
                                size="3",
                                background="rgba(255, 255, 255, 0.85)",
                                color="rgba(0, 0, 0, 0.85)",
                                border_radius="0.75rem",
                                font_weight="600",
                                padding_x="2rem",
                                padding_y="0.875rem",
                                _hover={"background": "rgba(255, 255, 255, 0.9)"},
                                transition="all 0.2s",
                            ),
                            href="/home",
                        ),
                        rx.link(
                            badge_button(
                                "Contact us",
                                size="3",
                                padding_x="2rem",
                                padding_y="0.875rem",
                            ),
                            href="/contact",
                        ),
                        spacing="4",
                        flex_direction=["column", "row"],
                    ),
                    align="center",
                    spacing="0",
                    z_index="10",
                    position="relative",
                ),
                max_width="80rem",
                width="100%",
                padding="4rem",
                background="rgba(255, 255, 255, 0.03)",
                backdrop_filter="blur(24px)",
                border="1px solid rgba(255, 255, 255, 0.05)",
                border_radius="3rem",
                position="relative",
                overflow="hidden",
                _before={
                    "content": '""',
                    "position": "absolute",
                    "inset": "0",
                    "background": "linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, transparent 100%)",
                    "opacity": "0.3",
                    "z_index": "0",
                },
            ),
            width="100%",
            padding_x="2rem",
            padding_y="8rem",
        ),
    )
