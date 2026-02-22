"""Framework cards and sidebar components."""

import reflex as rx

from .state import FrameworkState
from ...styles import (
    CARD_STYLE,
    white,
    purple,
    TEXT_PURPLE,
    TEXT_ACCENT,
)


def _skel(w: str, h: str) -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h), loading=True, style={"border_radius": "6px"}
    )


def skeleton_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.skeleton(
                    rx.box(width="31px", height="31px"),
                    loading=True,
                    style={"border_radius": "8px"},
                ),
                rx.spacer(),
                _skel("70px", "18px"),
                width="100%",
                align="center",
            ),
            rx.vstack(
                _skel("60%", "20px"),
                _skel("100%", "14px"),
                _skel("80%", "14px"),
                _skel("90%", "14px"),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            rx.vstack(
                rx.box(height="1px", width="100%", background=white(0.05)),
                rx.hstack(
                    rx.vstack(
                        _skel("45px", "10px"),
                        _skel("80px", "14px"),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    _skel("90px", "14px"),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        **CARD_STYLE,
    )


def category_filter_button(category):
    is_active = FrameworkState.active_category == category.value

    return rx.button(
        category.label,
        on_click=lambda: FrameworkState.set_active_category(category.value),
        size="2",
        style=rx.cond(
            is_active,
            {
                "background": purple(0.18),
                "border": f"1px solid {purple(0.5)}",
                "border_radius": "999px",
                "color": TEXT_PURPLE,
                "font_weight": "600",
                "font_size": "13px",
                "cursor": "pointer",
                "transition": "all 0.15s ease",
                "padding": "0 16px",
            },
            {
                "background": "transparent",
                "border": f"1px solid {white(0.1)}",
                "border_radius": "999px",
                "color": white(0.5),
                "font_weight": "500",
                "font_size": "13px",
                "cursor": "pointer",
                "transition": "all 0.15s ease",
                "padding": "0 16px",
                "_hover": {
                    "background": white(0.06),
                    "color": white(0.85),
                    "border_color": white(0.2),
                },
            },
        ),
    )


def framework_card(framework):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("trending-up", size=15, color=white(0.5)),
                    background=white(0.06),
                    border_radius="8px",
                    padding="8px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.spacer(),
                rx.badge(
                    framework.scope,
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                    style={
                        "border_radius": "6px",
                        "font_size": "10px",
                        "letter_spacing": "0.03em",
                    },
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(
                    framework.title,
                    size="4",
                    weight="bold",
                    color="white",
                    line_height="1.35",
                ),
                rx.text(
                    framework.description,
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
                width="100%",
            ),
            rx.spacer(),
            rx.vstack(
                rx.box(height="1px", width="100%", background=white(0.05)),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            size="1",
                            color=white(0.2),
                            weight="bold",
                            letter_spacing="0.08em",
                        ),
                        rx.text(
                            framework.author,
                            size="2",
                            color=white(0.6),
                            weight="medium",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.text(
                            "VIEW ASSETS", size="1", weight="bold", color=TEXT_ACCENT
                        ),
                        rx.icon("arrow-right", size=12, color=TEXT_ACCENT),
                        spacing="1",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        **CARD_STYLE,
        cursor="pointer",
        style={
            "transition": "all 0.15s ease",
            "_hover": {
                "background": white(0.045),
                "border_color": white(0.13),
                "transform": "translateY(-1px)",
            },
        },
    )
