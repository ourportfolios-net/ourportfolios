import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card
from ...styles import (
    white,
    purple,
    green,
    red,
    GREEN_LABEL,
    RED_LABEL,
    GREEN_FILL,
    GREEN_FADE,
    RED_FILL,
    RED_FADE,
    GREEN_BORDER,
    RED_BORDER,
    GREEN_BG,
    RED_BG,
    accent_btn,
)


def vnindex_mini_chart():
    return rx.cond(
        HomeState.vnindex_chart_data,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="normalized_close",
                stroke=purple(0.9),
                fill=purple(0.08),
                stroke_width=1.5,
            ),
            rx.recharts.x_axis(data_key="name", hide=True),
            rx.recharts.y_axis(domain=[0, 1], hide=True),
            data=HomeState.vnindex_chart_data,
            width=100,
            height=44,
        ),
        rx.box(width="100px", height="44px"),
    )


def _time_btn(label: str, active: bool = False) -> rx.Component:
    return rx.box(
        rx.text(
            label, size="1", weight="bold", color="white" if active else white(0.3)
        ),
        padding="0.2rem 0.5rem",
        border_radius="5px",
        background=white(0.08) if active else "transparent",
        cursor="pointer",
        _hover={"background": white(0.05), "color": white(0.6)} if not active else {},
        transition="all 0.15s ease",
    )


def _sector_bar(name: str, value: str, is_positive: bool = True) -> rx.Component:
    label_color = GREEN_LABEL if is_positive else RED_LABEL
    bar_fill = GREEN_FILL if is_positive else RED_FILL
    bar_fade = GREEN_FADE if is_positive else RED_FADE
    border = GREEN_BORDER if is_positive else RED_BORDER
    bg = GREEN_BG if is_positive else RED_BG

    return rx.box(
        rx.vstack(
            rx.text(name, size="1", weight="bold", color=label_color),
            rx.box(
                rx.box(
                    width="100%",
                    height="100%",
                    background=f"linear-gradient(180deg, {bar_fill} 0%, {bar_fade} 100%)",
                    border_radius="3px",
                ),
                width="100%",
                height="40px",
                border_radius="4px",
                overflow="hidden",
                background=white(0.02),
            ),
            rx.text(value, size="3", weight="bold", color="white"),
            spacing="1",
            align="center",
            width="100%",
        ),
        padding="0.625rem 0.875rem",
        border_radius="10px",
        background=bg,
        border=f"1px solid {border}",
        flex="1",
        min_width="80px",
    )


def _sector_chip(name: str, value: str, is_positive: bool = True) -> rx.Component:
    return rx.hstack(
        rx.text(name, size="1", weight="medium", color=white(0.35)),
        rx.badge(
            value,
            color_scheme="green" if is_positive else "gray",
            size="1",
            weight="bold",
        ),
        spacing="2",
        align="center",
    )


def market_overview_section():
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="5px",
                        height="5px",
                        border_radius="50%",
                        background=purple(0.8),
                    ),
                    rx.text(
                        "MARKET OVERVIEW",
                        size="1",
                        weight="bold",
                        color=white(0.35),
                        letter_spacing="0.08em",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    _time_btn("1D", active=True),
                    _time_btn("1W"),
                    _time_btn("1M"),
                    _time_btn("1Y"),
                    spacing="0",
                    padding="0.2rem",
                    border_radius="6px",
                    background=white(0.03),
                    border=f"1px solid {white(0.05)}",
                ),
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.text("VNIndex", size="1", color=white(0.35)),
                            rx.hstack(
                                rx.text(
                                    HomeState.vnindex_value,
                                    size="6",
                                    weight="bold",
                                    color="white",
                                    letter_spacing="-0.02em",
                                ),
                                rx.badge(
                                    HomeState.vnindex_change,
                                    color_scheme=rx.cond(
                                        HomeState.vnindex_is_positive, "green", "red"
                                    ),
                                    size="1",
                                    weight="bold",
                                ),
                                spacing="2",
                                align="end",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        vnindex_mini_chart(),
                        spacing="4",
                        align="center",
                    ),
                    padding="0.875rem 1rem",
                    border_radius="10px",
                    background=white(0.02),
                    border=f"1px solid {white(0.05)}",
                ),
                rx.hstack(
                    _sector_bar("BANKS", "+2.4%", is_positive=True),
                    _sector_bar("REAL EST", "-0.8%", is_positive=False),
                    rx.vstack(
                        _sector_chip("TECH", "+1.1%", is_positive=True),
                        _sector_chip("RETAIL", "0.0%", is_positive=True),
                        spacing="3",
                        justify="center",
                        height="100%",
                    ),
                    spacing="3",
                    align="stretch",
                    flex="1",
                ),
                spacing="4",
                width="100%",
                align="center",
            ),
            accent_btn("View Market", href="/market"),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        width="100%",
    )
