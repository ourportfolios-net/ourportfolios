"""Tickers page — viewport-fitted, no layout shift on view toggle."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.breadcrumb import breadcrumb
from ...styles import white, purple, TEXT_PURPLE

from .state import TickersPageState
from .controls import board_toolbar, compare_toolbar
from .compare_table import compare_table, empty_compare_state
from .ticker_board import new_ticker_board


def view_toggle():
    btn_active = {
        "background": purple(0.18),
        "border": f"1px solid {purple(0.5)}",
        "border_radius": "8px",
        "color": TEXT_PURPLE,
        "font_weight": "600",
        "font_size": "13px",
        "cursor": "pointer",
        "transition": "all 0.15s ease",
        "padding": "0 14px",
        "height": "34px",
    }
    btn_inactive = {
        "background": "transparent",
        "border": "1px solid transparent",
        "border_radius": "8px",
        "color": white(0.4),
        "font_weight": "500",
        "font_size": "13px",
        "cursor": "pointer",
        "transition": "all 0.15s ease",
        "padding": "0 14px",
        "height": "34px",
        "_hover": {"color": white(0.85), "background": white(0.05)},
    }
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
                TickersPageState.view_mode == "board", btn_active, btn_inactive
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
                TickersPageState.view_mode == "compare", btn_active, btn_inactive
            ),
        ),
        spacing="1",
        padding="3px",
        border_radius="10px",
        background=white(0.04),
        border=f"1px solid {white(0.08)}",
        flex_shrink="0",
    )


def page_header():
    """Compact two-line header — breadcrumb + title+subtitle inline with toggle."""
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
        # Height = viewport minus navbar (~60px) minus header (~90px) minus toolbar (~50px) minus gaps
        height="calc(100vh - 240px)",
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
                width="90vw",
                max_width="1800px",
                margin="0 auto",
            ),
            width="100%",
            padding_top="5em",  # clears navbar
            padding_x="0",
            padding_bottom="2em",
            height="100vh",
            overflow="hidden",  # page itself does NOT scroll — board scroll_area handles it
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background="#090909",
        color="white",
        height="100vh",
        width="100%",
        overflow="hidden",
    )
