"""Framework selection cards for the Home dashboard."""

from __future__ import annotations

import reflex as rx

from ....components.cards import glass_card
from ....state.framework_state import GlobalFrameworkState
from ....state.home_state import HomeState
from ....styles import PREVIEW_BOX_STYLE, accent_btn, icon_box, white
from .card_shell import (
    CARD_HEADER_HEIGHT,
    CARD_PREVIEW_SURFACE_HEIGHT,
    HUB_CARD_STYLE,
    HUB_CARD_TEXT_CLAMP,
    skeleton,
)

_CARD_STACK_HEIGHT = "12.5rem"


def _skeleton_row(icon_name: str, index: int) -> rx.Component:
    faded = rx.cond(HomeState.framework_hover_index == index, "0", "1")
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=15, color=white(0.2)),
                background=white(0.05),
                border=f"1px solid {white(0.06)}",
                border_radius="0.5rem",
                padding="0.4375rem",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
                opacity=faded,
                transition="opacity 0.3s ease",
            ),
            rx.vstack(
                skeleton("5.625rem", "0.75rem"),
                skeleton("100%", "1.25rem"),
                spacing="2",
                align="start",
                flex="1",
                overflow="hidden",
                opacity=faded,
                transition="opacity 0.3s ease",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.625rem 0.75rem",
        border_radius="0.5625rem",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
        width="100%",
        height=CARD_HEADER_HEIGHT,
    )


def _glass_row(icon_name: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(icon_name, size=15, color=white(0.55)),
            background=white(0.06),
            border=f"1px solid {white(0.08)}",
            border_radius="0.5rem",
            padding="0.4375rem",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="white"),
            rx.text(description, size="1", color=white(0.4), line_height="1.4"),
            spacing="0",
            align="start",
            flex="1",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.625rem 0.75rem",
    )


def _framework_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("3.75rem", "0.5625rem"),
            rx.box(
                rx.vstack(
                    _skeleton_row("shield", 0),
                    _skeleton_row("zap", 1),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        rx.box(
                            _glass_row(
                                "shield",
                                "Value Investing",
                                "Focuses on undervalued assets with strong fundamentals.",
                            ),
                            position="absolute",
                            top="0",
                            left="0",
                            right="0",
                            height=CARD_HEADER_HEIGHT,
                        ),
                        rx.box(
                            _glass_row(
                                "zap",
                                "Growth Strategy",
                                "Targets high-growth companies with expanding market share.",
                            ),
                            position="absolute",
                            top=f"calc({CARD_HEADER_HEIGHT} + 0.5rem)",
                            left="0",
                            right="0",
                            height=CARD_HEADER_HEIGHT,
                        ),
                        position="absolute",
                        top=rx.cond(
                            HomeState.framework_hover_index == 0,
                            "0",
                            f"calc(-{CARD_HEADER_HEIGHT} - 0.5rem)",
                        ),
                        left="0",
                        right="0",
                        height=f"calc({CARD_HEADER_HEIGHT} * 2 + 0.5rem)",
                        transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                    ),
                    position="absolute",
                    top=rx.cond(
                        HomeState.framework_hover_index == 0,
                        "0",
                        f"calc({CARD_HEADER_HEIGHT} + 0.5rem)",
                    ),
                    left="0",
                    right="0",
                    height=CARD_HEADER_HEIGHT,
                    background=white(0.05),
                    border_radius="0.5625rem",
                    border=f"1px solid {white(0.1)}",
                    overflow="hidden",
                    transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                    pointer_events="none",
                ),
                position="relative",
                width="100%",
                height=f"calc({CARD_HEADER_HEIGHT} * 2 + 0.5rem)",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def select_framework_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Select Framework", size="4", weight="bold", color="white"),
                    rx.text(
                        "Define your strategy. Choose from Growth, Value, or Dividend focused models.",
                        size="2",
                        color=white(0.38),
                        line_height="1.65",
                        style=HUB_CARD_TEXT_CLAMP,
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                ),
                icon_box("target", color="purple"),
                spacing="3",
                align="start",
                width="100%",
            ),
            _framework_preview(),
            rx.spacer(),
            accent_btn("Browse Frameworks", href="/framework"),
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
            z_index="0",
            cursor="pointer",
            on_click=rx.redirect("/framework"),
        ),
        **HUB_CARD_STYLE,
        on_mouse_enter=HomeState.start_framework_hover,
        on_mouse_leave=HomeState.stop_framework_hover,
    )


def selected_framework_card():
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework", size="1", weight="medium", color=white(0.35)
                ),
                rx.link(
                    rx.text(
                        GlobalFrameworkState.framework_display_name,
                        size="4",
                        weight="bold",
                        color="white",
                        line_height="1.35",
                    ),
                    href="/framework",
                    underline="none",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            size="1",
                            weight="bold",
                            color=white(0.2),
                            letter_spacing="0.08em",
                        ),
                        rx.text(
                            rx.cond(
                                GlobalFrameworkState.selected_framework.get("author"),
                                GlobalFrameworkState.selected_framework.get(
                                    "author", ""
                                ),
                                "—",
                            ),
                            size="2",
                            weight="medium",
                            color=white(0.5),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    accent_btn(
                        "Change", icon="refresh-cw", href="/framework", icon_left=True
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
        ),
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework", size="1", weight="medium", color=white(0.22)
                ),
                rx.vstack(
                    rx.text(
                        "No Framework Selected",
                        size="4",
                        weight="bold",
                        color=white(0.28),
                    ),
                    rx.text(
                        "Choose a framework to guide your analysis",
                        size="2",
                        color=white(0.18),
                        line_height="1.6",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.spacer(),
                accent_btn("Select Framework", href="/framework"),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
        ),
    )
