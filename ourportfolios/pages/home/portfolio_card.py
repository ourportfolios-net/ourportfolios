import reflex as rx
from ...state.home_state import HomeState
from ...styles import CARD_STYLE, white, green

_PREVIEW_H = "200px"


def _perf_bar(hover_width: str, hover_color: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="30px", height="11px", border_radius="4px", background=white(0.06)
        ),
        rx.box(
            rx.box(
                width=rx.cond(HomeState.is_portfolio_hovered, hover_width, "40%"),
                height="100%",
                background=rx.cond(
                    HomeState.is_portfolio_hovered, hover_color, white(0.08)
                ),
                border_radius="4px",
                transition="all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1)",
            ),
            width="100%",
            height="11px",
            background=white(0.04),
            border_radius="4px",
            overflow="hidden",
            flex="1",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def portfolio_card_with_hover():
    return rx.box(
        rx.vstack(
            # Header: title left, green icon right
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Manage Portfolio",
                        size="4",
                        weight="bold",
                        color="white",
                        line_height="1.3",
                    ),
                    rx.text(
                        "Track performance, view allocation and rebalance your current holdings.",
                        size="2",
                        color=white(0.38),
                        line_height="1.65",
                        style={
                            "display": "-webkit-box",
                            "-webkit-line-clamp": "3",
                            "-webkit-box-orient": "vertical",
                            "overflow": "hidden",
                        },
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                ),
                rx.box(
                    rx.icon(
                        "arrow-right-left", size=16, color="rgba(52, 211, 153, 0.9)"
                    ),
                    background=green(0.12),
                    border=f"1px solid {green(0.25)}",
                    border_radius="10px",
                    padding="9px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    flex_shrink="0",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            # Preview
            rx.box(
                rx.vstack(
                    rx.box(
                        width="60px",
                        height="9px",
                        border_radius="4px",
                        background=white(0.06),
                    ),
                    rx.hstack(
                        rx.text(
                            HomeState.portfolio_value,
                            font_size="18px",
                            font_weight="800",
                            letter_spacing="-0.02em",
                            style={"transition": "all 1s ease"},
                        ),
                        rx.spacer(),
                        rx.badge(
                            HomeState.portfolio_change,
                            color_scheme="green",
                            size="1",
                            font_weight="700",
                            style={"transition": "all 1s ease"},
                        ),
                        width="100%",
                        align="center",
                    ),
                    rx.vstack(
                        _perf_bar("68%", green(0.5)),
                        _perf_bar("42%", green(0.35)),
                        _perf_bar("28%", green(0.25)),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="0.75rem",
                border_radius="10px",
                background=white(0.02),
                border=f"1px solid {white(0.04)}",
                width="100%",
                height=_PREVIEW_H,
                overflow="hidden",
            ),
            # Footer button
            rx.box(
                rx.hstack(
                    rx.text(
                        "Open Portfolio Manager",
                        font_size="13px",
                        font_weight="700",
                        color=white(0.7),
                    ),
                    rx.icon("arrow-right", size=14, color=white(0.5)),
                    spacing="2",
                    align="center",
                    justify="center",
                    width="100%",
                ),
                width="100%",
                padding="0.6rem 1rem",
                border_radius="9px",
                background=white(0.03),
                border=f"1px solid {white(0.07)}",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": white(0.06), "border_color": white(0.12)},
                position="relative",
                z_index="2",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="1",
            cursor="pointer",
            on_click=HomeState.handle_portfolio,
        ),
        on_mouse_enter=HomeState.start_portfolio_hover,
        on_mouse_leave=HomeState.end_portfolio_hover,
        **CARD_STYLE,
        position="relative",
        overflow="hidden",
        style={
            "height": "420px",
            "transition": "all 0.15s ease",
            "_hover": {
                "background": white(0.045),
                "border_color": white(0.13),
                "transform": "translateY(-1px)",
            },
        },
    )
