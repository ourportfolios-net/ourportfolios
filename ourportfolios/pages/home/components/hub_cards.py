"""Comparison and portfolio cards for the Home dashboard."""

from __future__ import annotations

import reflex as rx

from ....state.home_state import HomeState
from ....styles import PREVIEW_BOX_STYLE, accent_btn, blue, green, white
from .card_shell import CARD_PREVIEW_SURFACE_HEIGHT, HUB_CARD_STYLE, skeleton


def _compare_col(color: str, is_hovered) -> rx.Component:
    return rx.box(
        rx.box(
            width="3.5rem", height="0.75rem", border_radius="0.25rem", background=color
        ),
        width=rx.cond(is_hovered, "3.5rem", "0px"),
        opacity=rx.cond(is_hovered, "1", "0"),
        overflow="hidden",
        transition="all 0.45s cubic-bezier(0.4, 0, 0.2, 1)",
    )


def _compare_row(col1: str, col2: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="3.5rem",
            height="1.25rem",
            border_radius="0.375rem",
            background=white(0.06),
        ),
        _compare_col(col1, HomeState.is_comparison_hovered),
        _compare_col(col2, HomeState.is_comparison_hovered),
        spacing="2",
        align="center",
        width="100%",
        padding="0.5rem 0.625rem",
        border_radius="0.5rem",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
    )


def _comparison_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("4.0625rem"),
            _compare_row(blue(0.45), white(0.08)),
            _compare_row(white(0.08), blue(0.45)),
            spacing="2",
            width="100%",
        ),
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def _perf_bar(hover_width: str, hover_color: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="1.875rem",
            height="0.6875rem",
            border_radius="0.25rem",
            background=white(0.06),
        ),
        rx.box(
            rx.box(
                width=rx.cond(HomeState.is_portfolio_hovered, hover_width, "40%"),
                height="100%",
                background=rx.cond(
                    HomeState.is_portfolio_hovered, hover_color, white(0.08)
                ),
                border_radius="0.25rem",
                transition="all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1)",
            ),
            width="100%",
            height="0.6875rem",
            background=white(0.04),
            border_radius="0.25rem",
            overflow="hidden",
            flex="1",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _portfolio_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("3.75rem"),
            rx.hstack(
                rx.text(
                    HomeState.portfolio_value,
                    size="5",
                    weight="bold",
                    letter_spacing="-0.02em",
                    style={"transition": "all 1s ease"},
                ),
                rx.spacer(),
                rx.badge(
                    HomeState.portfolio_change,
                    color_scheme="green",
                    size="1",
                    weight="bold",
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
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def _hub_card(
    title: str,
    description: str,
    icon: str,
    icon_color: str,
    preview: rx.Component,
    cta_label: str,
    on_click,
    on_hover_enter=None,
    on_hover_leave=None,
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(title, size="4", weight="bold", color="white"),
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
                    min_width="0",
                ),
                rx.box(
                    rx.icon(icon, size=16, color=white(0.55)),
                    background=white(0.06),
                    border=f"1px solid {white(0.08)}",
                    border_radius="0.625rem",
                    padding="0.5625rem",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    flex_shrink="0",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            preview,
            rx.spacer(),
            accent_btn(cta_label, on_click=on_click),
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
            on_click=on_click,
        ),
        **HUB_CARD_STYLE,
        on_mouse_enter=on_hover_enter,
        on_mouse_leave=on_hover_leave,
    )


def compare_assets_card() -> rx.Component:
    return _hub_card(
        title="Compare Assets",
        description="Head-to-head metrics. Analyze P/E, EPS, and Volatility side-by-side.",
        icon="git-compare",
        icon_color="blue",
        preview=_comparison_preview(),
        cta_label="Go to Comparison",
        on_click=HomeState.handle_compare,
        on_hover_enter=HomeState.start_comparison_hover,
        on_hover_leave=HomeState.end_comparison_hover,
    )


def manage_portfolio_card() -> rx.Component:
    return _hub_card(
        title="Manage Portfolio",
        description="Track performance, view allocation and rebalance your current holdings.",
        icon="arrow-right-left",
        icon_color="green",
        preview=_portfolio_preview(),
        cta_label="Open Portfolio",
        on_click=HomeState.handle_portfolio,
        on_hover_enter=HomeState.start_portfolio_hover,
        on_hover_leave=HomeState.end_portfolio_hover,
    )
