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

from ourportfolios.components.graph import pct_change_badge
from ourportfolios.pages.tickers.state import TickersPageState
from ourportfolios.state import TickerBoardState
from ourportfolios.state.cart_state import CartState
from ourportfolios.styles import (
    BTN_GHOST_XS,
    CARD_BG,
    CARD_BORDER,
    DIVIDER,
    TEXT_MUTED,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    white,
)

_COMPARE_BTN = {
    **BTN_GHOST_XS,
    "color": "rgba(139,92,246,0.55)",
    "_hover": {
        "background": "rgba(139,92,246,0.1)",
        "color": "rgba(139,92,246,0.9)",
        "border_color": "rgba(139,92,246,0.3)",
    },
}


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


def _compare_btn(symbol: str) -> rx.Component:
    return rx.button(
        rx.icon("between_horizontal_start", size=13),
        on_click=TickersPageState.add_ticker_to_compare(symbol),
        size="1",
        **_COMPARE_BTN,
    )


# ── Column definitions ─────────────────────────────────────────────────────────
# Each column: (label, sort_field, width).  Header and data rows both use this
# list so adding/removing a column only requires editing one place.

_COLUMNS = [
    ("Price", "current_price", "4.375rem"),
    ("Change", "pct_price_change", "4.6875rem"),
    ("Volume", "accumulated_volume", "4.375rem"),
    ("Mkt Cap", "market_cap", "4.6875rem"),
]

# Width reserved for the two trailing icon-buttons (cart + compare)
_ACTIONS_WIDTH = "4.5rem"


# ── Sort indicator ─────────────────────────────────────────────────────────────


def _sort_indicator(field: str) -> rx.Component:
    current = TickersPageState.sort_options[TickersPageState.selected_sort_option]
    return rx.cond(
        current == field,
        rx.cond(
            TickersPageState.selected_sort_order == "ASC",
            rx.icon("chevron-up", size=11, color=white(0.5)),
            rx.icon("chevron-down", size=11, color=white(0.5)),
        ),
        rx.fragment(),
    )


# ── Header row ─────────────────────────────────────────────────────────────────


def _header_cell(label: str, field: str, width: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(label, size="1", color=white(0.3), weight="medium"),
            _sort_indicator(field),
            spacing="1",
            align="center",
        ),
        on_click=lambda: TickersPageState.toggle_sort(field),
        cursor="pointer",
        user_select="none",
        width=width,
        display="flex",
        justify_content="flex-end",
        transition="opacity 0.12s ease",
        _hover={"opacity": "0.7"},
    )


def _header_row() -> rx.Component:
    return rx.hstack(
        # Symbol column — left-aligned, fills remaining space
        rx.box(
            rx.hstack(
                rx.text("Symbol", size="1", color=white(0.3), weight="medium"),
                _sort_indicator("symbol"),
                spacing="1",
                align="center",
            ),
            on_click=lambda: TickersPageState.toggle_sort("symbol"),
            cursor="pointer",
            user_select="none",
            flex="1",
            min_width="0",
            _hover={"opacity": "0.7"},
            transition="opacity 0.12s ease",
        ),
        rx.spacer(),
        rx.hstack(
            *[_header_cell(label, field, w) for label, field, w in _COLUMNS],
            rx.box(width=_ACTIONS_WIDTH, flex_shrink="0"),
            spacing="4",
            align="center",
            flex_shrink="0",
        ),
        align="center",
        width="100%",
        padding=_ROW_PADDING,
        border_bottom=f"1px solid {DIVIDER}",
    )


# ── Ticker row ─────────────────────────────────────────────────────────────────


def ticker_row(ticker: dict) -> rx.Component:
    """Single ticker row — mirrors search_bar suggestion_card layout."""
    symbol = ticker["symbol"].to(str)
    name = ticker.get("company_name", "").to(str)
    industry = ticker.get("industry", "").to(str)
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
                        # Industry badge — matches framework_cards.py badge style
                        rx.cond(
                            industry != "",
                            rx.badge(
                                industry,
                                variant="soft",
                                color_scheme="gray",
                                size="1",
                                border_radius="0.375rem",
                                font_size="0.625rem",
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
                            "max_width": "25rem",
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
            # RIGHT — data columns (widths match _COLUMNS)
            rx.hstack(
                rx.box(
                    rx.text(price, size="2", weight="medium", color=TEXT_SECONDARY),
                    width="4.375rem",
                    display="flex",
                    justify_content="flex-end",
                ),
                rx.box(
                    pct_change_badge(diff=pct),
                    width="4.6875rem",
                    display="flex",
                    justify_content="flex-end",
                ),
                rx.box(
                    _compact_number(volume),
                    width="4.375rem",
                    display="flex",
                    justify_content="flex-end",
                ),
                rx.box(
                    _compact_number(mktcap),
                    width="4.6875rem",
                    display="flex",
                    justify_content="flex-end",
                ),
                # Actions
                rx.hstack(
                    rx.box(
                        rx.tooltip(_cart_btn(symbol), content="Add to cart"),
                        on_click=rx.stop_propagation,
                        display="flex",
                        align_items="center",
                    ),
                    rx.box(
                        rx.tooltip(
                            _compare_btn(symbol), content="Add to comparison board",
                        ),
                        on_click=rx.stop_propagation,
                        display="flex",
                        align_items="center",
                    ),
                    spacing="2",
                    width=_ACTIONS_WIDTH,
                    justify_content="flex-end",
                    flex_shrink="0",
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


def _skel(w: str, h: str = "0.8125rem") -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h), loading=True, border_radius="0.3125rem",
    )


def _skeleton_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.hstack(
                _skel("5rem", "1.25rem"), _skel("2.5rem", "1.125rem"), spacing="2",
            ),
            _skel("12.5rem", "0.8125rem"),
            spacing="2",
        ),
        rx.spacer(),
        rx.hstack(
            _skel("3.125rem", "1rem"),
            _skel("4.0625rem", "1.25rem"),
            _skel("3.4375rem", "0.875rem"),
            _skel("3.125rem", "0.875rem"),
            _skel("2rem", "2rem"),
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
        border_radius="0.875rem",
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
                border_radius="0.875rem",
                background=CARD_BG,
                border=CARD_BORDER,
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text(
                "No tickers found", size="4", weight="medium", color=TEXT_SECONDARY,
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


_BOARD_H = "42em"


def new_ticker_board() -> rx.Component:
    """Ticker board — skeleton → row list → empty state."""
    return rx.cond(
        TickersPageState.is_board_loading,
        rx.box(skeleton_list(), height=_BOARD_H, overflow="hidden", width="100%"),
        rx.cond(
            TickerBoardState.get_all_tickers.length() > 0,
            rx.box(
                _header_row(),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(TickerBoardState.get_all_tickers, ticker_row),
                        spacing="0",
                        width="100%",
                    ),
                    scrollbars="vertical",
                    type="hover",
                    style={"flex": "1", "width": "100%"},
                ),
                border_radius="0.875rem",
                border=CARD_BORDER,
                background=CARD_BG,
                overflow="hidden",
                width="100%",
                height=_BOARD_H,
                display="flex",
                flex_direction="column",
            ),
            _empty_state(),
        ),
    )
