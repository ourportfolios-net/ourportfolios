"""Tickers page."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.breadcrumb import breadcrumb
from ...styles import (
    white,
    DIVIDER,
    PAGE_BG,
    overlay_style,
)

from .state import TickersPageState
from .controls import board_toolbar, compare_toolbar
from .compare_table import compare_table, empty_compare_state
from .ticker_board import new_ticker_board


# ── View toggle ────────────────────────────────────────────────────────────────


def _toggle_btn(label: str, icon_name: str, mode: str) -> rx.Component:
    is_active = TickersPageState.view_mode == mode
    return rx.button(
        rx.hstack(
            rx.icon(icon_name, size=13),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        on_click=TickersPageState.set_view_mode(mode),
        size="2",
        background=rx.cond(is_active, white(0.09), white(0.05)),
        border=rx.cond(
            is_active,
            f"1px solid {white(0.18)}",
            f"1px solid {white(0.1)}",
        ),
        color=rx.cond(is_active, white(0.9), white(0.6)),
        font_weight=rx.cond(is_active, "600", "500"),
        font_size="13px",
        border_radius="8px",
        cursor="pointer",
        transition="all 0.15s ease",
    )


def view_toggle():
    return rx.hstack(
        _toggle_btn("Board", "layout_dashboard", "board"),
        _toggle_btn("Compare", "between_horizontal_start", "compare"),
        spacing="2",
        flex_shrink="0",
    )


def page_header():
    return rx.vstack(
        breadcrumb("/tickers"),
        rx.hstack(
            rx.vstack(
                rx.heading("Tickers", size="7", weight="bold", color="white"),
                rx.text(
                    "Browse, filter and compare stocks across all markets.",
                    size="2",
                    color=white(0.38),
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            view_toggle(),
            width="100%",
            align="center",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def toolbar_row():
    _is_board = TickersPageState.view_mode == "board"
    _is_compare = TickersPageState.view_mode == "compare"
    return rx.hstack(
        rx.box(board_toolbar(), style=overlay_style(_is_board)),
        rx.box(compare_toolbar(), style=overlay_style(_is_compare)),
        rx.box(height="34px", flex="1"),
        width="100%",
        align="center",
        position="relative",
    )


def content_area():
    _is_board = TickersPageState.view_mode == "board"
    _is_compare = TickersPageState.view_mode == "compare"
    return rx.box(
        rx.box(new_ticker_board(), style=overlay_style(_is_board)),
        rx.box(
            rx.cond(
                TickersPageState.compare_list.length() > 0,
                compare_table(),
                empty_compare_state(),
            ),
            style=overlay_style(_is_compare),
        ),
        position="relative",
        width="100%",
        height="42em",
        flex_shrink="0",
    )


def main_content():
    return rx.vstack(
        page_header(),
        rx.box(height="1px", width="100%", background=DIVIDER),
        toolbar_row(),
        content_area(),
        spacing="4",
        width="100%",
    )


@rx.page(route="/tickers", on_load=TickersPageState.on_mount)
def index():
    return rx.box(
        navbar(),
        rx.box(
            rx.box(
                main_content(),
                width="86vw",
                max_width="1800px",
                margin="0 auto",
            ),
            width="100%",
            padding_top="5em",
            padding_bottom="1.8em",
            padding_x="0",
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background=PAGE_BG,
        color="white",
        min_height="100vh",
        width="100%",
    )
