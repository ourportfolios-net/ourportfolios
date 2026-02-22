import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card
from ...styles import (
    glow_orb_style,
    icon_box_style,
    SURFACE_CARD_STYLE,
    DECISION_HUB_HOVER,
    white,
    green,
)


def _perf_bar(
    hover_width: str, hover_color: str, idle_color: str = white(0.15)
) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="36px", height="14px", border_radius="4px", background=white(0.08)
        ),
        rx.box(
            rx.box(
                width=rx.cond(HomeState.is_portfolio_hovered, hover_width, "50%"),
                height="100%",
                background=rx.cond(
                    HomeState.is_portfolio_hovered, hover_color, idle_color
                ),
                border_radius="4px",
                transition="all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
            ),
            width="100%",
            height="14px",
            background=white(0.05),
            border_radius="4px",
            overflow="hidden",
            flex="1",
            max_width="calc(100% - 100px)",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def portfolio_card_with_hover():
    return rx.box(
        rx.box(**glow_orb_style("green")),
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Manage Portfolio", size="5", font_weight="700"),
                        rx.text(
                            "Track performance, view allocation and rebalance your current holdings.",
                            color=white(0.5),
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon("arrow-right-left", size=20, color="var(--green-9)"),
                        **icon_box_style("green"),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.box(flex="1"),
                rx.vstack(
                    rx.vstack(
                        rx.box(
                            width="80px",
                            height="10px",
                            border_radius="4px",
                            background=white(0.08),
                        ),
                        rx.hstack(
                            rx.text(
                                HomeState.portfolio_value,
                                font_size="18px",
                                font_weight="700",
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
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                        margin_bottom="0.75rem",
                    ),
                    rx.vstack(
                        _perf_bar("70%", green(0.5)),
                        _perf_bar("30%", green(0.35)),
                        _perf_bar("30%", green(0.35)),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="0",
                    **SURFACE_CARD_STYLE,
                ),
                rx.button(
                    "Open Portfolio Manager",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="outline",
                    on_click=HomeState.handle_portfolio,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                width="100%",
                height="100%",
            ),
            padding="1rem",
            width="100%",
            height="420px",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        on_mouse_enter=HomeState.start_portfolio_hover,
        on_mouse_leave=HomeState.end_portfolio_hover,
        **DECISION_HUB_HOVER,
    )
