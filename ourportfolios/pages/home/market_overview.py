import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card
from ...styles import white


def vnindex_mini_chart():
    return rx.cond(
        HomeState.vnindex_chart_data,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="normalized_close",
                stroke="rgba(139, 92, 246, 0.9)",
                fill="rgba(139, 92, 246, 0.08)",
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
            label,
            font_size="11px",
            font_weight="600",
            color="white" if active else white(0.3),
        ),
        padding="0.2rem 0.5rem",
        border_radius="5px",
        background=white(0.08) if active else "transparent",
        cursor="pointer",
        _hover={"background": white(0.05), "color": white(0.6)} if not active else {},
        transition="all 0.15s ease",
    )


def _sector_bar(name: str, value: str, is_positive: bool = True) -> rx.Component:
    bar_fill = "rgba(16, 185, 129, 0.5)" if is_positive else "rgba(239, 68, 68, 0.5)"
    bar_fade = "rgba(16, 185, 129, 0.08)" if is_positive else "rgba(239, 68, 68, 0.08)"
    label_color = "rgba(52, 211, 153, 1)" if is_positive else "rgba(248, 113, 113, 1)"
    border = "rgba(16, 185, 129, 0.12)" if is_positive else "rgba(239, 68, 68, 0.12)"
    bg = "rgba(16, 185, 129, 0.05)" if is_positive else "rgba(239, 68, 68, 0.05)"

    return rx.box(
        rx.vstack(
            rx.text(
                name,
                font_size="9px",
                font_weight="700",
                letter_spacing="0.08em",
                color=label_color,
            ),
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
            rx.text(value, font_size="13px", font_weight="700", color="white"),
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
        rx.text(name, font_size="10px", font_weight="500", color=white(0.35)),
        rx.badge(
            value,
            color_scheme="green" if is_positive else "gray",
            size="1",
            font_weight="700",
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
                        background="rgba(139, 92, 246, 0.8)",
                    ),
                    rx.text(
                        "MARKET OVERVIEW",
                        font_size="10px",
                        font_weight="700",
                        letter_spacing="0.08em",
                        color=white(0.35),
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
                            rx.text("VNIndex", font_size="11px", color=white(0.35)),
                            rx.hstack(
                                rx.text(
                                    HomeState.vnindex_value,
                                    font_size="22px",
                                    font_weight="800",
                                    color="white",
                                    letter_spacing="-0.02em",
                                ),
                                rx.badge(
                                    HomeState.vnindex_change,
                                    color_scheme=rx.cond(
                                        HomeState.vnindex_is_positive, "green", "red"
                                    ),
                                    size="1",
                                    font_weight="700",
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
            # Footer button - smaller and bottom right
            rx.box(
                rx.link(
                    rx.hstack(
                        rx.text(
                            "View Full Market Data",
                            font_size="11px",
                            font_weight="600",
                            color=white(0.7),
                        ),
                        rx.icon("arrow-right", size=12, color=white(0.5)),
                        spacing="1",
                        align="center",
                    ),
                    href="/market",
                    underline="none",
                ),
                width="auto",
                padding="0.45rem 0.75rem",
                border_radius="7px",
                background=white(0.03),
                border=f"1px solid {white(0.07)}",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": white(0.06), "border_color": white(0.12)},
                align_self="flex-end",
            ),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        width="100%",
    )
