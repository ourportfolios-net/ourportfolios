"""Bento grid section component."""

import reflex as rx

from ..components import scroll_reveal, magic_bento_card, shiny_text


def bento_section() -> rx.Component:
    """Bento grid section with feature cards."""
    return rx.center(
        rx.hstack(
            # Bento grid on the left
            scroll_reveal(
                rx.box(
                    # Overview card - top left square
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "layout-dashboard",
                                        size=22,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.75rem",
                                    height="2.75rem",
                                    border_radius="0.875rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Overview",
                                    size="4",
                                    font_weight="600",
                                    margin_bottom="0.25rem",
                                ),
                                rx.text(
                                    "Central data console.",
                                    font_size="0.8rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.4",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2rem",
                        width="14rem",
                        height="14rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 2"],
                        grid_row="1 / 2",
                    ),
                    # Automation card - top middle square
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "zap", size=22, color="rgba(255, 255, 255, 0.5)"
                                    ),
                                    width="2.75rem",
                                    height="2.75rem",
                                    border_radius="0.875rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Automation",
                                    size="4",
                                    font_weight="600",
                                    margin_bottom="0.25rem",
                                ),
                                rx.text(
                                    "Streamline every workflow.",
                                    font_size="0.8rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.4",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2rem",
                        width="14rem",
                        height="14rem",
                        grid_column=["1 / -1", "1 / -1", "2 / 3"],
                        grid_row="1 / 2",
                    ),
                    # Analytics card - tall rectangle spanning 2 columns and 2 rows
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "bar-chart-3",
                                        size=22,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.75rem",
                                    height="2.75rem",
                                    border_radius="0.875rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Analytics",
                                    size="4",
                                    font_weight="600",
                                    margin_bottom="0.25rem",
                                ),
                                rx.text(
                                    "Insights with pixel precision.",
                                    font_size="0.8rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.4",
                                ),
                                spacing="0",
                                align="start",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 3"],
                        grid_row="2 / 4",
                    ),
                    # Collaboration card - tall vertical rectangle spanning 2 rows
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "users",
                                        size=22,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.75rem",
                                    height="2.75rem",
                                    border_radius="0.875rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Collaboration",
                                    size="4",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Seamless teamwork across global borders.",
                                    font_size="0.8rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.4",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            align="start",
                            height="100%",
                        ),
                        padding="2rem",
                        width="14rem",
                        grid_column=["1 / -1", "1 / -1", "3 / 4"],
                        grid_row="1 / 3",
                    ),
                    # Security card - square at bottom right
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "shield",
                                        size=22,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.75rem",
                                    height="2.75rem",
                                    border_radius="0.875rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Security",
                                    size="4",
                                    font_weight="600",
                                    margin_bottom="0.25rem",
                                ),
                                rx.text(
                                    "Enterprise encryption.",
                                    font_size="0.8rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.4",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2rem",
                        width="14rem",
                        height="14rem",
                        grid_column=["1 / -1", "1 / -1", "3 / 4"],
                        grid_row="3 / 4",
                    ),
                    display="grid",
                    grid_template_columns=[
                        "1fr",
                        "1fr",
                        "14rem 14rem 14rem",
                    ],
                    grid_template_rows="14rem 7rem 14rem",
                    gap="1.25rem",
                    width="fit-content",
                ),
                delay=0.1,
            ),
            # Text content on the right
            scroll_reveal(
                rx.vstack(
                    shiny_text(
                        text="The Magic Bento",
                        speed=3,
                        color="rgba(255, 255, 255, 0.75)",
                        shine_color="rgba(255, 255, 255, 1)",
                        spread=120,
                        direction="left",
                        yoyo=False,
                        delay=0,
                        font_size=["2rem", "2.5rem", "3rem"],
                        font_weight="600",
                        line_height="1.2",
                        letter_spacing="-0.02em",
                        text_align="right",
                    ),
                    rx.text(
                        "Tools for the modern investor.",
                        font_size="1.125rem",
                        color="rgba(255, 255, 255, 0.4)",
                        font_weight="300",
                        line_height="1.5",
                        text_align="right",
                        margin_top="2rem",
                    ),
                    align="end",
                    max_width="28rem",
                    min_width="28rem",
                ),
                delay=0.2,
            ),
            align="center",
            justify="center",
            gap="3rem",
            width="fit-content",
            margin_left="2.5rem",
            padding_x="2.5rem",
            flex_direction=["column", "column", "row"],
        ),
        width="100%",
        padding_y="4rem",
        padding_x="2rem",
        display="flex",
        justify_content="flex-start",
    )
