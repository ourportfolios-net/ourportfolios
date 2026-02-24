"""Tickers allrounder page — consistent with framework page design."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...styles import white, purple, TEXT_PURPLE

from .state import TickersPageState
from .controls import board_toolbar, compare_toolbar
from .compare_table import compare_table, empty_compare_state
from .ticker_board import new_ticker_board


def breadcrumb():
    return rx.hstack(
        rx.html(
            "<style>.bc-home { color: rgba(255,255,255,0.35) !important; text-decoration: none !important; transition: color 0.15s ease; } .bc-home:hover { color: white !important; }</style>"
        ),
        rx.link("Home", href="/home", size="2", class_name="bc-home"),
        rx.icon("chevron-right", size=13, color="rgba(255,255,255,0.2)"),
        rx.text("Tickers", size="2", color="rgba(255,255,255,0.75)", weight="medium"),
        spacing="2",
        align="center",
    )


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
    )


def page_header():
    return rx.vstack(
        breadcrumb(),
        rx.heading("Tickers", size="8", weight="bold", color="white"),
        rx.text(
            "Browse, filter and compare stocks across all markets.",
            size="3",
            color="rgba(255,255,255,0.4)",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def toolbar_row():
    return rx.hstack(
        rx.cond(
            TickersPageState.view_mode == "board",
            board_toolbar(),
            compare_toolbar(),
        ),
        view_toggle(),
        width="100%",
        align="center",
        spacing="3",
    )


def board_view():
    return new_ticker_board()


def compare_view():
    return rx.cond(
        TickersPageState.compare_list.length() > 0,
        compare_table(),
        empty_compare_state(),
    )


def main_content():
    return rx.vstack(
        page_header(),
        rx.box(height="1px", width="100%", background=white(0.06)),
        toolbar_row(),
        rx.cond(
            TickersPageState.view_mode == "board",
            board_view(),
            compare_view(),
        ),
        spacing="5",
        width="100%",
    )


@rx.page(
    route="/tickers",
    on_load=TickersPageState.on_mount,
)
def index():
    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                main_content(),
                width="90vw",
                max_width="1800px",
            ),
            width="100%",
            padding="2em",
            padding_top="3em",
            padding_bottom="5em",
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
