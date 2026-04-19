"""Showcase section with CardSwap demo - Investment App Flow."""

import reflex as rx

from ourportfolios.pages.landing.components import (
    card,
    card_swap,
    scroll_reveal,
    shiny_text,
)


def _skeleton(
    width: str = "4rem",
    height: str = "0.75rem",
    opacity: float = 0.12,
    **kwargs: object,
) -> rx.Component:
    """Create a static skeleton placeholder (rounded rectangle)."""
    return rx.box(
        width=width,
        height=height,
        background=f"rgba(255, 255, 255, {opacity})",
        border_radius="0.25rem",
        flex_shrink="0",
        **kwargs,
    )


# Static data for the performance line charts (trending up)
_PERF_DATA_1 = [
    {"d": 1, "v": 20},
    {"d": 2, "v": 24},
    {"d": 3, "v": 22},
    {"d": 4, "v": 28},
    {"d": 5, "v": 32},
    {"d": 6, "v": 30},
    {"d": 7, "v": 36},
    {"d": 8, "v": 42},
]

_PERF_DATA_2 = [
    {"d": 1, "v": 15},
    {"d": 2, "v": 18},
    {"d": 3, "v": 16},
    {"d": 4, "v": 22},
    {"d": 5, "v": 20},
    {"d": 6, "v": 26},
    {"d": 7, "v": 30},
    {"d": 8, "v": 35},
]


def showcase_section() -> rx.Component:
    """Showcase section with CardSwap demo."""
    return scroll_reveal(
        rx.center(
            rx.box(
                rx.hstack(
                    rx.vstack(
                        shiny_text(
                            text="Investing simplified.",
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
                        ),
                        rx.text(
                            "Focus on what actually matters.",
                            font_size=["1rem", "1.125rem"],
                            color="rgba(255, 255, 255, 0.4)",
                            margin_top="2rem",
                            font_weight="300",
                            line_height="1.5",
                        ),
                        align="start",
                        spacing="0",
                        flex="1",
                        max_width="30rem",
                    ),
                    rx.box(
                        rx.box(
                            card_swap(
                                # Card 1: Framework Selection
                                card(
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(
                                                    "01",
                                                    font_size="0.875rem",
                                                    font_weight="600",
                                                    color="rgba(255, 255, 255, 0.3)",
                                                ),
                                                rx.heading(
                                                    "Select a Framework",
                                                    size="4",
                                                    font_weight="500",
                                                    letter_spacing="0.05em",
                                                    text_transform="uppercase",
                                                ),
                                                spacing="3",
                                                align="center",
                                            ),
                                            rx.text(
                                                "Choose your investment strategy",
                                                font_size="0.875rem",
                                                color="rgba(255, 255, 255, 0.5)",
                                                font_weight="300",
                                            ),
                                            spacing="1",
                                            align="start",
                                            padding="1.5rem",
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.center(
                                                rx.vstack(
                                                    rx.vstack(
                                                        # Selected framework row
                                                        rx.box(
                                                            rx.hstack(
                                                                rx.box(
                                                                    width="1rem",
                                                                    height="0.5rem",
                                                                    border_radius="0.125rem",
                                                                    background="#7C3AED",
                                                                    box_shadow="0 0 0.5rem rgba(124, 58, 237, 0.6)",
                                                                ),
                                                                _skeleton(
                                                                    width="7rem",
                                                                    height="1rem",
                                                                    opacity=0.25,
                                                                ),
                                                                spacing="3",
                                                                align="center",
                                                            ),
                                                            width="100%",
                                                            padding="1rem 1.25rem",
                                                            background="rgba(124, 58, 237, 0.1)",
                                                            border="1px solid rgba(124, 58, 237, 0.3)",
                                                            border_radius="0.75rem",
                                                        ),
                                                        # Unselected framework rows
                                                        rx.box(
                                                            rx.hstack(
                                                                rx.box(
                                                                    width="1rem",
                                                                    height="0.5rem",
                                                                    border_radius="0.125rem",
                                                                    background="rgba(255, 255, 255, 0.15)",
                                                                ),
                                                                _skeleton(
                                                                    width="6rem",
                                                                    height="1rem",
                                                                ),
                                                                spacing="3",
                                                                align="center",
                                                            ),
                                                            width="100%",
                                                            padding="1rem 1.25rem",
                                                            background="rgba(255, 255, 255, 0.02)",
                                                            border="1px solid rgba(255, 255, 255, 0.08)",
                                                            border_radius="0.75rem",
                                                        ),
                                                        rx.box(
                                                            rx.hstack(
                                                                rx.box(
                                                                    width="1rem",
                                                                    height="0.5rem",
                                                                    border_radius="0.125rem",
                                                                    background="rgba(255, 255, 255, 0.15)",
                                                                ),
                                                                _skeleton(
                                                                    width="8rem",
                                                                    height="1rem",
                                                                ),
                                                                spacing="3",
                                                                align="center",
                                                            ),
                                                            width="100%",
                                                            padding="1rem 1.25rem",
                                                            background="rgba(255, 255, 255, 0.02)",
                                                            border="1px solid rgba(255, 255, 255, 0.08)",
                                                            border_radius="0.75rem",
                                                        ),
                                                        rx.box(
                                                            rx.hstack(
                                                                rx.box(
                                                                    width="1rem",
                                                                    height="0.5rem",
                                                                    border_radius="0.125rem",
                                                                    background="rgba(255, 255, 255, 0.15)",
                                                                ),
                                                                _skeleton(
                                                                    width="5.5rem",
                                                                    height="1rem",
                                                                ),
                                                                spacing="3",
                                                                align="center",
                                                            ),
                                                            width="100%",
                                                            padding="1rem 1.25rem",
                                                            background="rgba(255, 255, 255, 0.02)",
                                                            border="1px solid rgba(255, 255, 255, 0.08)",
                                                            border_radius="0.75rem",
                                                        ),
                                                        spacing="2",
                                                        width="100%",
                                                    ),
                                                    align="center",
                                                    spacing="0",
                                                    width="100%",
                                                    max_width="22rem",
                                                ),
                                                width="100%",
                                                height="100%",
                                            ),
                                            padding="2rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="rgba(255, 255, 255, 0.03)",
                                        border="1px solid rgba(255, 255, 255, 0.07)",
                                        border_radius="0.875rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                # Card 2: Ticker Analysis
                                card(
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(
                                                    "02",
                                                    font_size="0.875rem",
                                                    font_weight="600",
                                                    color="rgba(255, 255, 255, 0.3)",
                                                ),
                                                rx.heading(
                                                    "Analyze",
                                                    size="4",
                                                    font_weight="500",
                                                    letter_spacing="0.05em",
                                                    text_transform="uppercase",
                                                ),
                                                spacing="3",
                                                align="center",
                                            ),
                                            rx.text(
                                                "Review key metrics and performance",
                                                font_size="0.875rem",
                                                color="rgba(255, 255, 255, 0.5)",
                                                font_weight="300",
                                            ),
                                            spacing="1",
                                            align="start",
                                            padding="1.5rem",
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                # Ticker header
                                                rx.hstack(
                                                    rx.vstack(
                                                        _skeleton(
                                                            width="3.5rem",
                                                            height="1.25rem",
                                                            opacity=0.18,
                                                        ),
                                                        _skeleton(
                                                            width="5rem",
                                                            height="0.75rem",
                                                            opacity=0.08,
                                                        ),
                                                        spacing="1",
                                                        align="start",
                                                    ),
                                                    rx.vstack(
                                                        _skeleton(
                                                            width="4.5rem",
                                                            height="1.25rem",
                                                            opacity=0.18,
                                                        ),
                                                        _skeleton(
                                                            width="2.5rem",
                                                            height="0.75rem",
                                                            opacity=0.15,
                                                        ),
                                                        spacing="1",
                                                        align="end",
                                                    ),
                                                    justify="between",
                                                    width="100%",
                                                ),
                                                # Key metrics grid
                                                rx.hstack(
                                                    rx.box(
                                                        rx.vstack(
                                                            _skeleton(
                                                                width="2rem",
                                                                height="0.7rem",
                                                                opacity=0.1,
                                                            ),
                                                            _skeleton(
                                                                width="3rem",
                                                                height="1.1rem",
                                                                opacity=0.18,
                                                            ),
                                                            spacing="2",
                                                            align="start",
                                                        ),
                                                        flex="1",
                                                        padding="0.875rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                                        border_radius="0.625rem",
                                                    ),
                                                    rx.box(
                                                        rx.vstack(
                                                            _skeleton(
                                                                width="2.5rem",
                                                                height="0.7rem",
                                                                opacity=0.1,
                                                            ),
                                                            _skeleton(
                                                                width="3rem",
                                                                height="1.1rem",
                                                                opacity=0.18,
                                                            ),
                                                            spacing="2",
                                                            align="start",
                                                        ),
                                                        flex="1",
                                                        padding="0.875rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                                        border_radius="0.625rem",
                                                    ),
                                                    rx.box(
                                                        rx.vstack(
                                                            _skeleton(
                                                                width="1.75rem",
                                                                height="0.7rem",
                                                                opacity=0.1,
                                                            ),
                                                            _skeleton(
                                                                width="3rem",
                                                                height="1.1rem",
                                                                opacity=0.18,
                                                            ),
                                                            spacing="2",
                                                            align="start",
                                                        ),
                                                        flex="1",
                                                        padding="0.875rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                                        border_radius="0.625rem",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                ),
                                                # Performance line charts (2 side-by-side)
                                                rx.hstack(
                                                    rx.box(
                                                        rx.vstack(
                                                            rx.text(
                                                                "Performance",
                                                                font_size="0.65rem",
                                                                color="rgba(255, 255, 255, 0.5)",
                                                            ),
                                                            rx.recharts.line_chart(
                                                                rx.recharts.line(
                                                                    data_key="v",
                                                                    stroke="#7C3AED",
                                                                    type_="monotone",
                                                                    dot=False,
                                                                    stroke_width=2.5,
                                                                ),
                                                                rx.recharts.x_axis(
                                                                    data_key="d",
                                                                    hide=True,
                                                                ),
                                                                rx.recharts.y_axis(
                                                                    hide=True,
                                                                ),
                                                                data=_PERF_DATA_1,
                                                                margin={
                                                                    "top": 4,
                                                                    "right": 4,
                                                                    "bottom": 0,
                                                                    "left": 4,
                                                                },
                                                                width="100%",
                                                                height=56,
                                                            ),
                                                            spacing="1",
                                                        ),
                                                        flex="1",
                                                        padding="0.75rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                                        border_radius="0.75rem",
                                                    ),
                                                    rx.box(
                                                        rx.vstack(
                                                            rx.text(
                                                                "Growth",
                                                                font_size="0.65rem",
                                                                color="rgba(255, 255, 255, 0.5)",
                                                            ),
                                                            rx.recharts.line_chart(
                                                                rx.recharts.line(
                                                                    data_key="v",
                                                                    stroke="rgba(255, 255, 255, 0.35)",
                                                                    type_="monotone",
                                                                    dot=False,
                                                                    stroke_width=2.5,
                                                                ),
                                                                rx.recharts.x_axis(
                                                                    data_key="d",
                                                                    hide=True,
                                                                ),
                                                                rx.recharts.y_axis(
                                                                    hide=True,
                                                                ),
                                                                data=_PERF_DATA_2,
                                                                margin={
                                                                    "top": 4,
                                                                    "right": 4,
                                                                    "bottom": 0,
                                                                    "left": 4,
                                                                },
                                                                width="100%",
                                                                height=56,
                                                            ),
                                                            spacing="1",
                                                        ),
                                                        flex="1",
                                                        padding="0.75rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                                        border_radius="0.75rem",
                                                    ),
                                                    spacing="2",
                                                    width="100%",
                                                ),
                                                spacing="3",
                                                width="100%",
                                            ),
                                            padding="1.5rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="rgba(255, 255, 255, 0.03)",
                                        border="1px solid rgba(255, 255, 255, 0.07)",
                                        border_radius="0.875rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                # Card 3: Portfolio Rebalancing
                                card(
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text(
                                                    "03",
                                                    font_size="0.875rem",
                                                    font_weight="600",
                                                    color="rgba(255, 255, 255, 0.3)",
                                                ),
                                                rx.heading(
                                                    "Rebalance",
                                                    size="4",
                                                    font_weight="500",
                                                    letter_spacing="0.05em",
                                                    text_transform="uppercase",
                                                ),
                                                spacing="3",
                                                align="center",
                                            ),
                                            rx.text(
                                                "Optimize your portfolio allocation",
                                                font_size="0.875rem",
                                                color="rgba(255, 255, 255, 0.5)",
                                                font_weight="300",
                                            ),
                                            spacing="1",
                                            align="start",
                                            padding="1.5rem",
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                # Portfolio allocation
                                                rx.box(
                                                    rx.vstack(
                                                        rx.hstack(
                                                            rx.text(
                                                                "Current Portfolio",
                                                                font_size="0.75rem",
                                                                color="rgba(255, 255, 255, 0.5)",
                                                            ),
                                                            _skeleton(
                                                                width="4.5rem",
                                                                height="1rem",
                                                                opacity=0.18,
                                                            ),
                                                            spacing="2",
                                                            justify="between",
                                                            width="100%",
                                                        ),
                                                        # Progress bars
                                                        rx.box(
                                                            rx.hstack(
                                                                rx.box(
                                                                    width="45%",
                                                                    height="100%",
                                                                    background="rgba(255, 255, 255, 0.3)",
                                                                    border_radius="0.15rem 0 0 0.15rem",
                                                                ),
                                                                rx.box(
                                                                    width="30%",
                                                                    height="100%",
                                                                    background="rgba(255, 255, 255, 0.2)",
                                                                ),
                                                                rx.box(
                                                                    width="25%",
                                                                    height="100%",
                                                                    background="rgba(255, 255, 255, 0.15)",
                                                                    border_radius="0 0.15rem 0.15rem 0",
                                                                ),
                                                                spacing="0",
                                                                width="100%",
                                                                height="100%",
                                                            ),
                                                            width="100%",
                                                            height="0.75rem",
                                                            background="rgba(255, 255, 255, 0.05)",
                                                            border_radius="0.15rem",
                                                            overflow="hidden",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    width="100%",
                                                    padding="1rem",
                                                    background="rgba(255, 255, 255, 0.02)",
                                                    border="1px solid rgba(255, 255, 255, 0.08)",
                                                    border_radius="0.75rem",
                                                ),
                                                # Rebalance suggestions
                                                rx.box(
                                                    rx.vstack(
                                                        rx.text(
                                                            "Recommended",
                                                            font_size="0.75rem",
                                                            color="rgba(255, 255, 255, 0.5)",
                                                            margin_bottom="0.5rem",
                                                        ),
                                                        rx.hstack(
                                                            rx.box(
                                                                rx.text(
                                                                    "↑",
                                                                    font_size="1rem",
                                                                    color="rgba(255, 255, 255, 0.6)",
                                                                ),
                                                                width="1.5rem",
                                                                height="1.5rem",
                                                                background="rgba(255, 255, 255, 0.08)",
                                                                border_radius="0.375rem",
                                                                display="flex",
                                                                align_items="center",
                                                                justify_content="center",
                                                            ),
                                                            rx.vstack(
                                                                _skeleton(
                                                                    width="5rem",
                                                                    height="0.85rem",
                                                                    opacity=0.15,
                                                                ),
                                                                _skeleton(
                                                                    width="2rem",
                                                                    height="0.7rem",
                                                                    opacity=0.2,
                                                                ),
                                                                spacing="1",
                                                                align="start",
                                                            ),
                                                            spacing="2",
                                                            align="center",
                                                            width="100%",
                                                        ),
                                                        rx.hstack(
                                                            rx.box(
                                                                rx.text(
                                                                    "↓",
                                                                    font_size="1rem",
                                                                    color="rgba(255, 255, 255, 0.4)",
                                                                ),
                                                                width="1.5rem",
                                                                height="1.5rem",
                                                                background="rgba(255, 255, 255, 0.05)",
                                                                border_radius="0.375rem",
                                                                display="flex",
                                                                align_items="center",
                                                                justify_content="center",
                                                            ),
                                                            rx.vstack(
                                                                _skeleton(
                                                                    width="6rem",
                                                                    height="0.85rem",
                                                                    opacity=0.12,
                                                                ),
                                                                _skeleton(
                                                                    width="1.5rem",
                                                                    height="0.7rem",
                                                                    opacity=0.1,
                                                                ),
                                                                spacing="1",
                                                                align="start",
                                                            ),
                                                            spacing="2",
                                                            align="center",
                                                            width="100%",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    width="100%",
                                                    padding="1rem",
                                                    background="rgba(255, 255, 255, 0.02)",
                                                    border="1px solid rgba(255, 255, 255, 0.08)",
                                                    border_radius="0.75rem",
                                                ),
                                                # Daily update badge
                                                rx.hstack(
                                                    rx.box(
                                                        width="0.75rem",
                                                        height="0.5rem",
                                                        background="#7C3AED",
                                                        border_radius="0.1rem",
                                                        box_shadow="0 0 0.375rem rgba(124, 58, 237, 0.8)",
                                                    ),
                                                    _skeleton(
                                                        width="6rem",
                                                        height="0.75rem",
                                                        opacity=0.1,
                                                    ),
                                                    spacing="2",
                                                    align="center",
                                                    justify="center",
                                                ),
                                                spacing="3",
                                                width="100%",
                                            ),
                                            padding="1.5rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="rgba(255, 255, 255, 0.03)",
                                        border="1px solid rgba(255, 255, 255, 0.07)",
                                        border_radius="0.875rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                width=550,
                                height=400,
                                card_distance=40,
                                vertical_distance=45,
                                delay=4000,
                                pause_on_hover=True,
                                skew_amount=0,
                                easing="elastic",
                            ),
                            style={"transformStyle": "preserve-3d"},
                        ),
                        width=["100%", "100%", "40.625rem"],
                        max_width="40.625rem",
                        min_height="37.5rem",
                        display="flex",
                        justify_content="center",
                        align_items="flex-start",
                        padding_top="2rem",
                        margin_left=["0", "0", "3rem"],
                    ),
                    spacing="0",
                    align="center",
                    width="100%",
                    max_width="87.5rem",
                    padding_x=["1.5rem", "2rem", "4rem"],
                    justify="center",
                    gap=["4rem", "5rem", "6rem"],
                    flex_direction=["column", "column", "row"],
                ),
                width="100%",
                display="flex",
                justify_content="center",
                overflow="hidden",
            ),
            width="100%",
            padding_y="1rem",
            margin_top="1rem",
        ),
    )
