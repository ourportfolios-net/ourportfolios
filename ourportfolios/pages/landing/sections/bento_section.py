"""Bento grid section component."""

import reflex as rx

from ourportfolios.pages.landing.components import scroll_reveal, shiny_text
from ourportfolios.pages.landing.components.bento_cards import (
    conciseness_card,
    focused_card,
    instructiveness_card,
    reliability_card,
    transparency_card,
)
from ourportfolios.ui.theme.colors import white


def bento_section() -> rx.Component:
    """Bento grid section with interactive feature cards."""
    return rx.center(
        rx.hstack(
            scroll_reveal(
                rx.box(
                    instructiveness_card(
                        grid_column=["1 / -1", "1 / -1", "1 / 3"],
                        grid_row="2 / 4",
                    ),
                    transparency_card(
                        width="14rem",
                        grid_column=["1 / -1", "1 / -1", "3 / 4"],
                        grid_row="1 / 3",
                    ),
                    reliability_card(
                        width="14rem",
                        height="14rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 2"],
                        grid_row="1 / 2",
                    ),
                    conciseness_card(
                        width="14rem",
                        height="14rem",
                        grid_column=["1 / -1", "1 / -1", "2 / 3"],
                        grid_row="1 / 2",
                    ),
                    focused_card(
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
                        text="ourleverage",
                        speed=3,
                        color=white(0.75),
                        shine_color=white(1),
                        spread=120,
                        direction="left",
                        yoyo=False,
                        delay=0,
                        font_size=["2rem", "2.5rem", "3rem"],
                        font_weight="600",
                        line_height="1.2",
                        letter_spacing="-0.02em",
                        text_align=["center", "center", "right"],
                    ),
                    rx.text(
                        "Experience our core values.",
                        font_size="1.125rem",
                        color=white(0.4),
                        font_weight="300",
                        line_height="1.5",
                        text_align=["center", "center", "right"],
                        margin_top="0.5rem",
                    ),
                    align="center",
                    max_width="28rem",
                ),
                delay=0.2,
            ),
            align="center",
            justify="center",
            gap="3rem",
            width=["100%", "100%", "fit-content"],
            margin_left="0",
            padding_x="2.5rem",
            flex_direction=["column", "column", "row"],
        ),
        width="100%",
        padding_y="4rem",
        padding_x="2rem",
        display="flex",
        justify_content="center",
    )
