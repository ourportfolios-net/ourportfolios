import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card
from ...styles import (
    glow_orb_style,
    icon_box_style,
    icon_color,
    SURFACE_CARD_STYLE,
    DECISION_HUB_HOVER,
    white,
    blue,
)


def _sliding_box(color_bg: str, is_hovered) -> rx.Component:
    return rx.box(
        rx.box(width="70px", height="16px", border_radius="4px", background=color_bg),
        width=rx.cond(is_hovered, "70px", "0px"),
        opacity=rx.cond(is_hovered, "1", "0"),
        overflow="hidden",
        transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
    )


def _skel_box(w: str, h: str) -> rx.Component:
    return rx.box(width=w, height=h, border_radius="4px", background=white(0.08))


def _compare_row(ticker_h: str, val1_color: str, val2_color: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="70px", height="24px", border_radius="6px", background=white(0.08)
        ),
        _sliding_box(val1_color, HomeState.is_comparison_hovered),
        _sliding_box(val2_color, HomeState.is_comparison_hovered),
        spacing="3",
        align="center",
        width="100%",
        padding="0.6rem",
        border_radius="8px",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
    )


def _comparison_visualization() -> rx.Component:
    return rx.box(
        rx.vstack(
            _skel_box("80px", "11px"),
            _compare_row("", blue(0.3), white(0.1)),
            _compare_row("", white(0.1), blue(0.3)),
            spacing="2",
            width="100%",
            style={"margin_bottom": "0.5rem"},
        ),
        **SURFACE_CARD_STYLE,
    )


def decision_hub_card(
    title: str,
    description: str,
    icon: str,
    color: str,
    button_text: str,
    button_variant: str,
    on_click,
    has_comparison_chart: bool = False,
    **_,
):
    return rx.box(
        rx.box(**glow_orb_style(color)),
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading(title, size="5", font_weight="700"),
                        rx.text(
                            description,
                            color=white(0.5),
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon(icon, size=20, color=icon_color(color)),
                        **icon_box_style(color),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.box(flex="1"),
                rx.cond(has_comparison_chart, _comparison_visualization()),
                rx.button(
                    button_text,
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant=button_variant,
                    on_click=on_click,
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
        on_mouse_enter=HomeState.start_comparison_hover,
        on_mouse_leave=HomeState.end_comparison_hover,
        **DECISION_HUB_HOVER,
    )
