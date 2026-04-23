"""Ticker board — row-based list."""

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

_COMPARE_BTN: dict[str, object] = {
    **BTN_GHOST_XS,
    "color": "rgba(139,92,246,0.55)",
    "_hover": {
        "background": "rgba(139,92,246,0.1)",
        "color": "rgba(139,92,246,0.9)",
        "border_color": "rgba(139,92,246,0.3)",
    },
}

_SKELETON_ROW_COUNT = 12
_BOARD_H = "42em"

# Fixed column widths
_W_PRICE = "4.5rem"
_W_CHANGE = "5rem"
_W_VOL = "4.375rem"
_W_CAP = "4.6875rem"
_W_ACT = "2.5rem"  # mobile: cart only
_W_ACT_SM = "4.75rem"  # sm+: cart + compare

_PAD_X = rx.breakpoints(initial="0.75em", md="1.25em")
_PAD_Y = "0.85em"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _compact_number(val: float) -> rx.Component:
    return rx.cond(
        val > 0,
        rx.text(f"{val}", size="2", color=TEXT_SECONDARY),
        rx.text("—", size="2", color=TEXT_MUTED),
    )


def _cart_btn(symbol: str) -> rx.Component:
    return rx.button(
        rx.icon("shopping-cart", size=13),
        on_click=[rx.stop_propagation, CartState.add_item(symbol)],
        size="1",
        style=BTN_GHOST_XS,
    )


def _compare_btn(symbol: str) -> rx.Component:
    return rx.button(
        rx.icon("between_horizontal_start", size=13),
        on_click=[rx.stop_propagation, TickersPageState.add_ticker_to_compare(symbol)],
        size="1",
        style=_COMPARE_BTN,
    )


def _skel(w: str, h: str = "0.8125rem") -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        border_radius="0.3125rem",
    )


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


def _hdr(
    label: str,
    field: str,
    width: str,
    *,
    hide_mobile: bool = False,
) -> rx.Component:
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
        min_width=width,
        flex_shrink="0",
        display=rx.breakpoints(initial="none" if hide_mobile else "flex", sm="flex"),
        justify_content="flex-end",
        transition="opacity 0.12s ease",
        _hover={"opacity": "0.7"},
    )


def _header_row() -> rx.Component:
    return rx.hstack(
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
            transition="opacity 0.12s ease",
            _hover={"opacity": "0.7"},
        ),
        rx.hstack(
            _hdr("Price", "current_price", _W_PRICE, hide_mobile=False),
            _hdr("Change", "pct_price_change", _W_CHANGE, hide_mobile=False),
            _hdr("Volume", "accumulated_volume", _W_VOL, hide_mobile=True),
            _hdr("Mkt Cap", "market_cap", _W_CAP, hide_mobile=True),
            rx.box(
                width=rx.breakpoints(initial=_W_ACT, sm=_W_ACT_SM),
                min_width=rx.breakpoints(initial=_W_ACT, sm=_W_ACT_SM),
                flex_shrink="0",
            ),
            spacing="3",
            align="center",
            flex_shrink="0",
        ),
        align="center",
        width="100%",
        padding_x=_PAD_X,
        padding_y=_PAD_Y,
        border_bottom=f"1px solid {DIVIDER}",
    )


# ── Ticker row ─────────────────────────────────────────────────────────────────


def ticker_row(ticker: dict) -> rx.Component:
    symbol = ticker["symbol"].to(str)
    name = ticker.get("company_name", "").to(str)
    industry = ticker.get("industry", "").to(str)
    price = ticker.get("current_price", 0).to(float)
    pct = ticker.get("pct_price_change", 0).to(float)
    volume = ticker.get("accumulated_volume", 0).to(float)
    mktcap = ticker.get("market_cap", 0).to(float)

    return rx.box(
        rx.hstack(
            # LEFT — identity
            rx.vstack(
                rx.hstack(
                    # Symbol wrapped in rx.link so right-click → open in new tab
                    rx.link(
                        rx.text(
                            symbol,
                            size="5",
                            weight="medium",
                            white_space="nowrap",
                        ),
                        href=f"/tickers/{symbol}",
                        text_decoration="none",
                        color="inherit",
                        # Stop propagation so the link click doesn't also fire
                        # the outer box's on_click redirect.
                        on_click=rx.stop_propagation,
                    ),
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
                            max_width=rx.breakpoints(initial="5rem", sm="7rem"),
                            overflow="hidden",
                            text_overflow="ellipsis",
                            white_space="nowrap",
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    align="center",
                    overflow="hidden",
                    max_width="100%",
                ),
                rx.text(
                    name,
                    size="2",
                    color=TEXT_TERTIARY,
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    max_width=rx.breakpoints(
                        initial="6rem",
                        xs="9rem",
                        sm="14rem",
                        md="22rem",
                    ),
                ),
                spacing="1",
                align="start",
                flex="1",
                min_width="0",
                overflow="hidden",
            ),
            # RIGHT — data + actions
            rx.hstack(
                # Price — always
                rx.box(
                    rx.text(price, size="2", weight="medium", color=TEXT_SECONDARY),
                    width=_W_PRICE,
                    min_width=_W_PRICE,
                    flex_shrink="0",
                    display="flex",
                    justify_content="flex-end",
                ),
                # Change — always
                rx.box(
                    pct_change_badge(diff=pct),
                    width=_W_CHANGE,
                    min_width=_W_CHANGE,
                    flex_shrink="0",
                    display="flex",
                    justify_content="flex-end",
                ),
                # Volume — sm+
                rx.box(
                    _compact_number(volume),
                    width=_W_VOL,
                    min_width=_W_VOL,
                    flex_shrink="0",
                    display=rx.breakpoints(initial="none", sm="flex"),
                    justify_content="flex-end",
                ),
                # Mkt Cap — sm+
                rx.box(
                    _compact_number(mktcap),
                    width=_W_CAP,
                    min_width=_W_CAP,
                    flex_shrink="0",
                    display=rx.breakpoints(initial="none", sm="flex"),
                    justify_content="flex-end",
                ),
                # Actions — stop_propagation prevents row navigation
                rx.hstack(
                    rx.tooltip(_cart_btn(symbol), content="Add to cart"),
                    rx.box(
                        rx.tooltip(
                            _compare_btn(symbol),
                            content="Add to comparison",
                        ),
                        display=rx.breakpoints(initial="none", sm="flex"),
                        align_items="center",
                    ),
                    spacing="1",
                    width=rx.breakpoints(initial=_W_ACT, sm=_W_ACT_SM),
                    min_width=rx.breakpoints(initial=_W_ACT, sm=_W_ACT_SM),
                    flex_shrink="0",
                    justify_content="flex-end",
                ),
                spacing="3",
                align="center",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding_x=_PAD_X,
            padding_y=_PAD_Y,
            overflow="hidden",
        ),
        # Row-level click navigates; action buttons stop propagation before
        # this fires so they don't cause navigation.
        on_click=rx.redirect(f"/tickers/{symbol}"),
        cursor="pointer",
        width="100%",
        border_bottom=f"1px solid {DIVIDER}",
        transition="background 0.12s ease",
        _hover={"background": white(0.03)},
        overflow="hidden",
    )


# ── Skeleton ───────────────────────────────────────────────────────────────────


def _skeleton_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.hstack(_skel("4rem", "1.25rem"), _skel("4rem", "1rem"), spacing="2"),
            _skel("7rem", "0.75rem"),
            spacing="2",
            flex="1",
            min_width="0",
        ),
        rx.hstack(
            _skel(_W_PRICE, "1rem"),
            _skel(_W_CHANGE, "1.25rem"),
            rx.box(
                _skel(_W_VOL, "0.875rem"),
                display=rx.breakpoints(initial="none", sm="block"),
            ),
            rx.box(
                _skel(_W_CAP, "0.875rem"),
                display=rx.breakpoints(initial="none", sm="block"),
            ),
            _skel("2rem", "2rem"),
            spacing="3",
            align="center",
            flex_shrink="0",
        ),
        align="center",
        width="100%",
        padding_x=_PAD_X,
        padding_y=_PAD_Y,
        border_bottom=f"1px solid {DIVIDER}",
    )


def skeleton_list() -> rx.Component:
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
                "No tickers found",
                size="4",
                weight="medium",
                color=TEXT_SECONDARY,
            ),
            rx.text(
                "Try adjusting your search or filters.",
                size="2",
                color=TEXT_TERTIARY,
                text_align="center",
            ),
            rx.cond(
                TickerBoardState.cache_error != "",
                rx.text(
                    TickerBoardState.cache_error,
                    size="1",
                    color=white(0.45),
                    text_align="center",
                ),
                rx.fragment(),
            ),
            rx.button(
                "Retry",
                on_click=[
                    TickerBoardState.load_tickers,
                    TickersPageState.auto_load_data,
                ],
                size="1",
                style=BTN_GHOST_XS,
            ),
            spacing="3",
            align="center",
        ),
        height="18em",
    )


# ── Public export ──────────────────────────────────────────────────────────────


def new_ticker_board() -> rx.Component:
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
