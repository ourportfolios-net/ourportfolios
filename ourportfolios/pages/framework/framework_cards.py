"""Framework cards and sidebar components."""

import reflex as rx

from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.styles import (
    CARD_STYLE,
    PILL_TOGGLE,
    PILL_TOGGLE_ACTIVE,
    accent_btn,
    white,
)


def _skel(w: str, h: str) -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        border_radius="0.375rem",
    )


def skeleton_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.skeleton(
                    rx.box(width="1.9375rem", height="1.9375rem"),
                    loading=True,
                    border_radius="0.5rem",
                ),
                rx.spacer(),
                _skel("4.375rem", "1.125rem"),
                width="100%",
                align="center",
            ),
            rx.vstack(
                _skel("60%", "1.25rem"),
                _skel("100%", "0.875rem"),
                _skel("80%", "0.875rem"),
                _skel("90%", "0.875rem"),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            rx.vstack(
                rx.box(height="1px", width="100%", background=white(0.05)),
                rx.hstack(
                    rx.vstack(
                        _skel("2.8125rem", "0.625rem"),
                        _skel("5rem", "0.875rem"),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    _skel("5.625rem", "0.875rem"),
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


def category_filter_button(category: object) -> rx.Component:
    is_active = FrameworkState.active_category == category.value

    return rx.cond(
        is_active,
        rx.button(
            category.label,
            on_click=lambda: FrameworkState.set_active_category(category.value),
            size="2",
            **PILL_TOGGLE_ACTIVE,
        ),
        rx.button(
            category.label,
            on_click=lambda: FrameworkState.set_active_category(category.value),
            size="2",
            **PILL_TOGGLE,
        ),
    )


def framework_card(framework: object) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("trending-up", size=15, color=white(0.5)),
                    background=white(0.06),
                    border_radius="0.5rem",
                    padding="0.5rem",
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
                    border_radius="0.375rem",
                    font_size="0.625rem",
                    letter_spacing="0.03em",
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
                    display="-webkit-box",
                    overflow="hidden",
                    style={
                        "-webkit-line-clamp": "3",
                        "-webkit-box-orient": "vertical",
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
                    accent_btn("View Framework"),
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
        transition="all 0.15s ease",
        _hover={
            "background": white(0.045),
            "border_color": white(0.13),
            "transform": "translateY(-1px)",
        },
    )
