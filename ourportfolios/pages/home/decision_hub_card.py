import reflex as rx
from ...state.home_state import HomeState
from ...styles import CARD_STYLE, white, blue

_PREVIEW_H = "200px"


def _skel_box(w: str, h: str) -> rx.Component:
    return rx.box(width=w, height=h, border_radius="4px", background=white(0.06))


def _compare_col(color: str, is_hovered) -> rx.Component:
    return rx.box(
        rx.box(width="56px", height="12px", border_radius="4px", background=color),
        width=rx.cond(is_hovered, "56px", "0px"),
        opacity=rx.cond(is_hovered, "1", "0"),
        overflow="hidden",
        transition="all 0.45s cubic-bezier(0.4, 0, 0.2, 1)",
    )


def _compare_row(val1_color: str, val2_color: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="56px", height="20px", border_radius="6px", background=white(0.06)
        ),
        _compare_col(val1_color, HomeState.is_comparison_hovered),
        _compare_col(val2_color, HomeState.is_comparison_hovered),
        spacing="2",
        align="center",
        width="100%",
        padding="0.5rem 0.625rem",
        border_radius="8px",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
    )


def _comparison_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            _skel_box("65px", "9px"),
            _compare_row(blue(0.45), white(0.08)),
            _compare_row(white(0.08), blue(0.45)),
            spacing="2",
            width="100%",
        ),
        padding="0.75rem",
        border_radius="10px",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
        width="100%",
        height=_PREVIEW_H,
        overflow="hidden",
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
    # Blue icon tint
    icon_color_val = "rgba(96, 165, 250, 0.9)"
    icon_bg = blue(0.12)
    icon_border = blue(0.25)

    return rx.box(
        rx.vstack(
            # Header: title left, blue icon right
            rx.hstack(
                rx.vstack(
                    rx.text(
                        title, size="4", weight="bold", color="white", line_height="1.3"
                    ),
                    rx.text(
                        description,
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
                    rx.icon(icon, size=16, color=icon_color_val),
                    background=icon_bg,
                    border=f"1px solid {icon_border}",
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
            rx.cond(
                has_comparison_chart,
                _comparison_preview(),
                rx.box(
                    width="100%",
                    height=_PREVIEW_H,
                    border_radius="10px",
                    background=white(0.02),
                    border=f"1px solid {white(0.04)}",
                ),
            ),
            rx.spacer(),
            # Footer button - smaller and bottom right
            rx.box(
                rx.hstack(
                    rx.text(
                        button_text,
                        font_size="11px",
                        font_weight="600",
                        color=white(0.7),
                    ),
                    rx.icon("arrow-right", size=12, color=white(0.5)),
                    spacing="1",
                    align="center",
                ),
                width="auto",
                padding="0.45rem 0.75rem",
                border_radius="7px",
                background=white(0.03),
                border=f"1px solid {white(0.07)}",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": white(0.06), "border_color": white(0.12)},
                position="relative",
                z_index="2",
                align_self="flex-end",
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
            on_click=on_click,
        ),
        **CARD_STYLE,
        position="relative",
        overflow="hidden",
        on_mouse_enter=HomeState.start_comparison_hover,
        on_mouse_leave=HomeState.end_comparison_hover,
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
