"""Ticker board — row-based list.

Each row mirrors the search_bar suggestion_card layout:
  LEFT:  Symbol (size 5, medium) + exchange badge + company name
  RIGHT: Price · pct_change_badge · volume · mkt cap · cart

Reuses pct_change_badge from components/graph.py — the same component
used in search_bar.py — for change indicators.  Badge styling matches
framework_cards.py (variant="soft", color_scheme="gray", border_radius="6px").
All tokens come from styles.py.
"""

import reflex as rx

from ...components.graph import pct_change_badge
from ...state import TickerBoardState
from ...state.cart_state import CartState
from ...styles import (
    white,
    CARD_BG,
    CARD_BORDER,
    DIVIDER,
    BTN_GHOST_XS,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    TEXT_MUTED,
)
from .state import TickersPageState


# ── Constants ──────────────────────────────────────────────────────────────────

_SKELETON_ROW_COUNT = 12
_ROW_PADDING = "0.85em 1.25em"


# ── Display helpers ────────────────────────────────────────────────────────────


def _compact_number(val, size: str = "2") -> rx.Component:
    """Format a number with K/M/B/T suffix — uses TEXT_SECONDARY."""
    return rx.cond(
        val >= 1_000_000_000_000,
        rx.text(f"{val / 1_000_000_000_000:.1f}T", size=size, color=TEXT_SECONDARY),
        rx.cond(
            val >= 1_000_000_000,
            rx.text(f"{val / 1_000_000_000:.1f}B", size=size, color=TEXT_SECONDARY),
            rx.cond(
                val >= 1_000_000,
                rx.text(f"{val / 1_000_000:.1f}M", size=size, color=TEXT_SECONDARY),
                rx.cond(
                    val >= 1_000,
                    rx.text(f"{val / 1_000:.0f}K", size=size, color=TEXT_SECONDARY),
                    rx.cond(
                        val > 0,
                        rx.text(val, size=size, color=TEXT_SECONDARY),
                        rx.text("—", size=size, color=TEXT_MUTED),
                    ),
                ),
            ),
        ),
    )


# ── Cart button ────────────────────────────────────────────────────────────────


def _cart_btn(symbol: str) -> rx.Component:
    """Cart icon — uses BTN_GHOST_XS from styles.py."""
    return rx.button(
        rx.icon("shopping-cart", size=13),
        on_click=CartState.add_item(symbol),
        size="1",
        **BTN_GHOST_XS,
    )


# ── Ticker row ─────────────────────────────────────────────────────────────────


def ticker_row(ticker: dict) -> rx.Component:
    """Single ticker row — mirrors search_bar suggestion_card layout."""
    symbol = ticker["symbol"].to(str)
    name = ticker.get("company_name", "").to(str)
    exchange = ticker.get("exchange", "").to(str)
    price = ticker.get("current_price", 0).to(float)
    pct = ticker.get("pct_price_change", 0).to(float)
    volume = ticker.get("accumulated_volume", 0).to(float)
    mktcap = ticker.get("market_cap", 0).to(float)

    return rx.box(
        rx.hstack(
            # LEFT — identity (matches search_bar.suggestion_card)
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        # Symbol — size="5", weight="medium" (same as search_bar)
                        rx.text(symbol, size="5", weight="medium"),
                        # Exchange badge — matches framework_cards.py badge style
                        rx.cond(
                            exchange != "",
                            rx.badge(
                                exchange,
                                variant="soft",
                                color_scheme="gray",
                                size="1",
                                border_radius="6px",
                                font_size="10px",
                                letter_spacing="0.03em",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        name,
                        size="2",
                        color=TEXT_TERTIARY,
                        style={
                            "white_space": "nowrap",
                            "overflow": "hidden",
                            "text_overflow": "ellipsis",
                            "max_width": "400px",
                        },
                    ),
                    spacing="1",
                    align="start",
                ),
                flex="1",
                min_width="0",
                overflow="hidden",
            ),
            rx.spacer(),
            # RIGHT — data + cart
            rx.hstack(
                # Price
                rx.text(price, size="3", weight="medium", color=TEXT_SECONDARY),
                # Change — reuses pct_change_badge from components/graph.py
                pct_change_badge(diff=pct),
                # Volume — icon + tooltip for context, no text label
                rx.tooltip(
                    rx.hstack(
                        rx.icon("bar-chart-3", size=11, color=TEXT_MUTED),
                        _compact_number(volume),
                        spacing="1",
                        align="center",
                    ),
                    content="Volume",
                ),
                # Market cap — icon + tooltip for context, no text label
                rx.tooltip(
                    rx.hstack(
                        rx.icon("landmark", size=11, color=TEXT_MUTED),
                        _compact_number(mktcap),
                        spacing="1",
                        align="center",
                    ),
                    content="Market Cap",
                ),
                # Cart
                rx.box(
                    _cart_btn(symbol),
                    on_click=rx.stop_propagation,
                    display="flex",
                    align_items="center",
                ),
                spacing="4",
                align="center",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding=_ROW_PADDING,
        ),
        on_click=rx.redirect(f"/tickers/{symbol}"),
        cursor="pointer",
        width="100%",
        border_bottom=f"1px solid {DIVIDER}",
        transition="background 0.12s ease",
        _hover={"background": white(0.03)},
    )


# ── Skeleton row ───────────────────────────────────────────────────────────────


def _skel(w: str, h: str = "13px") -> rx.Component:
    return rx.skeleton(rx.box(width=w, height=h), loading=True, border_radius="5px")


def _skeleton_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.hstack(_skel("80px", "20px"), _skel("40px", "18px"), spacing="2"),
            _skel("200px", "13px"),
            spacing="2",
        ),
        rx.spacer(),
        rx.hstack(
            _skel("50px", "16px"),
            _skel("65px", "20px"),
            _skel("55px", "14px"),
            _skel("50px", "14px"),
            _skel("32px", "32px"),
            spacing="4",
            align="center",
        ),
        align="center",
        width="100%",
        padding=_ROW_PADDING,
        border_bottom=f"1px solid {DIVIDER}",
    )


def skeleton_list() -> rx.Component:
    """Skeleton rows shown during initial data load."""
    return rx.box(
        rx.vstack(
            *[_skeleton_row() for _ in range(_SKELETON_ROW_COUNT)],
            spacing="0",
            width="100%",
        ),
        border_radius="14px",
        border=CARD_BORDER,
        background=CARD_BG,
        overflow="hidden",
        width="100%",
    )


# ── Empty state ────────────────────────────────────────────────────────────────


def _empty_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("search-x", size=28, color=TEXT_MUTED),
                padding="1.25em",
                border_radius="14px",
                background=CARD_BG,
                border=CARD_BORDER,
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text(
                "No tickers found", size="4", weight="medium", color=TEXT_SECONDARY
            ),
            rx.text(
                "Try adjusting your search or filters.",
                size="2",
                color=TEXT_TERTIARY,
                text_align="center",
            ),
            spacing="3",
            align="center",
        ),
        height="18em",
    )


# ── Public export ──────────────────────────────────────────────────────────────


def new_ticker_board() -> rx.Component:
    """Ticker board — skeleton → row list → empty state."""
    return rx.cond(
        TickersPageState.is_board_loading,
        skeleton_list(),
        rx.cond(
            TickerBoardState.get_all_tickers.length() > 0,
            rx.box(
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(TickerBoardState.get_all_tickers, ticker_row),
                        spacing="0",
                        width="100%",
                    ),
                    scrollbars="vertical",
                    type="hover",
                    style={"height": "calc(100vh - 280px)", "width": "100%"},
                ),
                border_radius="14px",
                border=CARD_BORDER,
                background=CARD_BG,
                overflow="hidden",
                width="100%",
            ),
            _empty_state(),
        ),
    )
