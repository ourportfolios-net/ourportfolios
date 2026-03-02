"""Tickers page — viewport-fitted, no layout shift on view toggle."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...styles import white, purple, TEXT_PURPLE

from .state import TickersPageState
from .controls import (
    board_toolbar,
    compare_toolbar,
    BTN_ICON_SECONDARY,
    BTN_VIEW_ACTIVE,
    BTN_VIEW_INACTIVE,
)
from .compare_table import compare_table, empty_compare_state
from .ticker_board import new_ticker_board


def breadcrumb():
    return rx.hstack(
        rx.html(
            "<style>"
            ".bc-home { color: rgba(255,255,255,0.35) !important; text-decoration: none !important; transition: color 0.15s ease; }"
            ".bc-home:hover { color: white !important; }"
            "</style>"
        ),
        rx.link("Home", href="/home", size="2", class_name="bc-home"),
        rx.icon("chevron-right", size=13, color="rgba(255,255,255,0.2)"),
        rx.text("Tickers", size="2", color="rgba(255,255,255,0.75)", weight="medium"),
        spacing="2",
        align="center",
    )


def view_toggle():
    return rx.hstack(
        rx.button(
            rx.hstack(
                rx.icon("layout-grid", size=13),
                rx.text("Board"),
                spacing="2",
                align="center",
            ),
            on_click=TickersPageState.set_view_mode("board"),
            size="2",
            style=rx.cond(
                TickersPageState.view_mode == "board",
                BTN_VIEW_ACTIVE,
                BTN_VIEW_INACTIVE,
            ),
        ),
        rx.button(
            rx.hstack(
                rx.icon("bar-chart-2", size=13),
                rx.text("Compare"),
                spacing="2",
                align="center",
            ),
            on_click=TickersPageState.set_view_mode("compare"),
            size="2",
            style=rx.cond(
                TickersPageState.view_mode == "compare",
                BTN_VIEW_ACTIVE,
                BTN_VIEW_INACTIVE,
            ),
        ),
        spacing="2",
        flex_shrink="0",
    )


def page_header():
    """Compact two-line header — breadcrumb + title+subtitle inline with toggle."""
    return rx.vstack(
        breadcrumb(),
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
    """
    Fixed-height toolbar row. Both toolbars are rendered but only the active
    one is visible — this prevents the row from reflowing when switching views.
    """
    return rx.hstack(
        # Board toolbar — hidden (opacity+pointer-events) when in compare mode
        rx.box(
            board_toolbar(),
            style={
                "flex": "1",
                "opacity": rx.cond(TickersPageState.view_mode == "board", "1", "0"),
                "pointer_events": rx.cond(
                    TickersPageState.view_mode == "board", "auto", "none"
                ),
                "transition": "opacity 0.15s ease",
                "position": "absolute",
                "left": "0",
                "top": "0",
                "right": "0",
            },
        ),
        # Compare toolbar — hidden when in board mode
        rx.box(
            compare_toolbar(),
            style={
                "flex": "1",
                "opacity": rx.cond(TickersPageState.view_mode == "compare", "1", "0"),
                "pointer_events": rx.cond(
                    TickersPageState.view_mode == "compare", "auto", "none"
                ),
                "transition": "opacity 0.15s ease",
                "position": "absolute",
                "left": "0",
                "top": "0",
                "right": "0",
            },
        ),
        # Invisible spacer to hold the row height regardless of which toolbar shows
        rx.box(height="34px", flex="1"),
        width="100%",
        align="center",
        position="relative",
    )


def content_area():
    """
    Both views are always in the DOM; only the active one is visible.
    This kills the layout shift entirely — dimensions stay constant.
    """
    return rx.box(
        # Board view
        rx.box(
            new_ticker_board(),
            style={
                "opacity": rx.cond(TickersPageState.view_mode == "board", "1", "0"),
                "pointer_events": rx.cond(
                    TickersPageState.view_mode == "board", "auto", "none"
                ),
                "transition": "opacity 0.15s ease",
                "position": "absolute",
                "inset": "0",
            },
        ),
        # Compare view
        rx.box(
            rx.cond(
                TickersPageState.compare_list.length() > 0,
                compare_table(),
                empty_compare_state(),
            ),
            style={
                "opacity": rx.cond(TickersPageState.view_mode == "compare", "1", "0"),
                "pointer_events": rx.cond(
                    TickersPageState.view_mode == "compare", "auto", "none"
                ),
                "transition": "opacity 0.15s ease",
                "position": "absolute",
                "inset": "0",
            },
        ),
        position="relative",
        flex="1",
        min_height="0",
        width="100%",
    )


def main_content():
    return rx.vstack(
        page_header(),
        rx.box(height="1px", width="100%", background=white(0.06)),
        toolbar_row(),
        content_area(),
        spacing="4",
        width="100%",
        flex="1",
        min_height="0",
        overflow="hidden",
    )


@rx.page(
    route="/tickers",
    on_load=TickersPageState.on_mount,
)
def index():
    return rx.box(
        navbar(),
        rx.box(
            rx.box(
                main_content(),
                width="86vw",
                max_width="1800px",
                margin="0 auto",
                display="flex",
                flex_direction="column",
                height="100%",
            ),
            width="100%",
            padding_top="5em",  # clears navbar
            padding_x="0",
            display="flex",
            flex_direction="column",
            flex="1",
            min_height="0",
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background="#090909",
        color="white",
        height="100vh",
        width="100%",
        display="flex",
        flex_direction="column",
        overflow="hidden",
    )
