"""Tickers page."""

import reflex as rx

from ourportfolios.components.breadcrumb import breadcrumb
from ourportfolios.components.drawer import drawer_button
from ourportfolios.components.navbar import navbar
from ourportfolios.pages.tickers.compare_table import compare_table, empty_compare_state
from ourportfolios.pages.tickers.controls import board_toolbar, compare_toolbar
from ourportfolios.pages.tickers.state import TickersPageState
from ourportfolios.pages.tickers.ticker_board import new_ticker_board
from ourportfolios.ui.primitives import secondary_button
from ourportfolios.ui.theme import PAGE_BG, overlay_style, white


def _toggle_button(label: str, icon_name: str, mode: str) -> rx.Component:
    is_active = TickersPageState.view_mode == mode
    return secondary_button(
        rx.hstack(
            rx.icon(icon_name, size=13),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        active=is_active,
        on_click=TickersPageState.set_view_mode(mode),
        size="2",
        flex_shrink="0",
    )


def view_toggle() -> rx.Component:
    return rx.hstack(
        _toggle_button("Board", "layout_dashboard", "board"),
        _toggle_button("Compare", "between_horizontal_start", "compare"),
        spacing="2",
        flex_shrink="0",
    )


def page_header() -> rx.Component:
    return rx.vstack(
        breadcrumb("/tickers"),
        rx.hstack(
            rx.vstack(
                rx.heading(
                    "Tickers",
                    size=rx.breakpoints(initial="6", md="7"),
                    weight="bold",
                    color="white",
                ),
                rx.text(
                    "Browse, filter and compare stocks across all markets.",
                    size="2",
                    color=white(0.38),
                ),
                spacing="1",
                align="start",
                flex="1",
                min_width="0",
            ),
            view_toggle(),
            align="center",
            width="100%",
            spacing="3",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def toolbar_row() -> rx.Component:
    """Wrap both toolbars in overlapping absolute boxes.

    Using a plain rx.box (not rx.hstack with fixed height) so the active
    toolbar can grow vertically on mobile without clipping.
    """
    _is_board = TickersPageState.view_mode == "board"
    _is_compare = TickersPageState.view_mode == "compare"
    return rx.box(
        rx.box(board_toolbar(), style=overlay_style(_is_board)),
        rx.box(compare_toolbar(), style=overlay_style(_is_compare)),
        position="relative",
        width="100%",
        # min-height prevents the container collapsing when both overlays are opacity:0
        min_height="2.5rem",
    )


def content_area() -> rx.Component:
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


def main_content() -> rx.Component:
    return rx.vstack(
        page_header(),
        toolbar_row(),
        content_area(),
        spacing="4",
        width="100%",
    )


@rx.page(route="/tickers", on_load=TickersPageState.on_mount)
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.box(
                main_content(),
                # Full width on mobile with padding; constrained vw on large screens
                width=rx.breakpoints(initial="100%", lg="86vw"),
                max_width="90rem",
                margin="0 auto",
                padding_x=rx.breakpoints(initial="1rem", lg="0"),
            ),
            width="100%",
            padding_top=rx.breakpoints(initial="4em", md="5em"),
            padding_bottom="1.8em",
            # Prevent inner content from creating a page-level horizontal scrollbar
            overflow_x="hidden",
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background=PAGE_BG,
        color="white",
        min_height="100vh",
        width="100%",
        # Hard-stop any horizontal overflow at the root
        overflow_x="hidden",
    )
