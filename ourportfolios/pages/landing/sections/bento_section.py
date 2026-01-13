"""Bento grid section component."""

import reflex as rx

from ..components import scroll_reveal, magic_bento_card


def bento_section() -> rx.Component:
    """Bento grid section with feature cards."""
    return rx.center(
        rx.vstack(
            scroll_reveal(
                rx.vstack(
                    rx.heading(
                        "The Magic Bento",
                        size="8",
                        font_weight="600",
                        letter_spacing="-0.02em",
                        margin_bottom="1.5rem",
                    ),
                    rx.text(
                        "Simple, focused tools designed for the modern investor and developer.",
                        font_size="1.125rem",
                        color="rgba(255, 255, 255, 0.4)",
                        font_weight="300",
                        line_height="1.5",
                    ),
                    align="center",
                    max_width="32rem",
                    margin_bottom="4rem",
                ),
            ),
            scroll_reveal(
                rx.box(
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "bar-chart-3",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Analytics",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Insights with pixel precision.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 3"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "layout-dashboard",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Overview",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Central data console.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "3 / 5"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "zap", size=24, color="rgba(255, 255, 255, 0.5)"
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Automation",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Streamline every workflow.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "users",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="2rem",
                            ),
                            rx.heading(
                                "Collaboration",
                                size="6",
                                font_weight="600",
                                margin_bottom="1rem",
                            ),
                            rx.text(
                                "Seamless teamwork across global borders with real-time syncing.",
                                font_size="1rem",
                                color="rgba(255, 255, 255, 0.3)",
                                max_width="17.5rem",
                                line_height="1.5",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        padding="3rem",
                        min_height="25rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 5"],
                        position="relative",
                        overflow="hidden",
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.hstack(
                                rx.center(
                                    rx.icon(
                                        "shield",
                                        size=20,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.5rem",
                                    height="2.5rem",
                                    border_radius="0.75rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                rx.heading(
                                    "Security",
                                    size="4",
                                    font_weight="600",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.text(
                                "Enterprise encryption.",
                                font_size="0.75rem",
                                color="rgba(255, 255, 255, 0.3)",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="11.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.hstack(
                                rx.center(
                                    rx.icon(
                                        "plug",
                                        size=20,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.5rem",
                                    height="2.5rem",
                                    border_radius="0.75rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                rx.heading(
                                    "Connect",
                                    size="4",
                                    font_weight="600",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.text(
                                "Universal API access.",
                                font_size="0.75rem",
                                color="rgba(255, 255, 255, 0.3)",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="11.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    display="grid",
                    grid_template_columns=["1fr", "1fr", "repeat(6, 1fr)"],
                    gap="1.5rem",
                    width="100%",
                    max_width="80rem",
                ),
                delay=0.1,
            ),
            align="center",
            width="100%",
            padding_x="1.5rem",
        ),
        width="100%",
        padding_y="10rem",
    )
