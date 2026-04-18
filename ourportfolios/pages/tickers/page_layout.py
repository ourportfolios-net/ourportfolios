"""Page layout components for the tickers page.

Contains the header, view toggle, toolbar, content area,
and main_content composition — all non-route helpers.
"""

import reflex as rx

from ourportfolios.components.breadcrumb import breadcrumb
from ourportfolios.pages.tickers.compare_table import compare_table, empty_compare_state
from ourportfolios.pages.tickers.controls import board_toolbar, compare_toolbar
from ourportfolios.pages.tickers.state import TickersPageState
from ourportfolios.pages.tickers.ticker_board import new_ticker_board
from ourportfolios.styles import BTN_SECONDARY, BTN_SECONDARY_ACTIVE, white

# ── View toggle ────────────────────────────────────────────────────────────────
# Uses BTN_SECONDARY / BTN_SECONDARY_ACTIVE — same tokens as Sort & Filter.


def _toggle_btn(label: str, icon_name: str, mode: str) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icon_name, size=14),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        on_click=TickersPageState.set_view_mode(mode),
        size="2",
        style=rx.cond(
            TickersPageState.view_mode == mode,
            BTN_SECONDARY_ACTIVE,
            BTN_SECONDARY,
        ),
    )


def view_toggle() -> rx.Component:
    return rx.hstack(
        _toggle_btn("Board", "layout_dashboard", "board"),
        _toggle_btn("Compare", "between_horizontal_start", "compare"),
        spacing="2",
        flex_shrink="0",
    )


# ── Page sections ──────────────────────────────────────────────────────────────


def page_header() -> rx.Component:
    """Header — breadcrumb + title/subtitle with view toggle."""
    return rx.vstack(
        breadcrumb("/tickers"),
        rx.hstack(
            rx.vstack(
                rx.heading("Tickers", size="8", weight="bold", color="white"),
                rx.text(
                    "Browse, filter and compare stocks across all markets.",
                    size="3",
                    color=white(0.4),
                ),
                spacing="2",
                align="start",
            ),
            rx.spacer(),
            view_toggle(),
            width="100%",
            align="center",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def toolbar_row() -> rx.Component:
    """Toolbar — swaps between board and compare controls."""
    return rx.cond(
        TickersPageState.view_mode == "board",
        board_toolbar(),
        compare_toolbar(),
    )


def content_area() -> rx.Component:
    """Board list or compare table."""
    return rx.cond(
        TickersPageState.view_mode == "board",
        new_ticker_board(),
        rx.cond(
            TickersPageState.compare_list.length() > 0,
            compare_table(),
            empty_compare_state(),
        ),
    )


def main_content() -> rx.Component:
    """Full page body below the navbar."""
    return rx.vstack(
        page_header(),
        rx.box(height="1px", width="100%", background=white(0.06)),
        toolbar_row(),
        content_area(),
        spacing="5",
        width="100%",
    )
