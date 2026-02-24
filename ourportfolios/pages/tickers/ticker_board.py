"""
New ticker board — uses only what TickerBoardState actually exposes:
  - get_all_tickers: list[dict]  keys: symbol, company_name, exchange, industry,
                                       current_price, pct_price_change,
                                       accumulated_volume, market_cap
  - _cache_loaded: bool (private — not usable as rx.var directly)

Cart is handled via CartState (accessed from the drawer/global state).
"""

import reflex as rx

from ...state import TickerBoardState
from ...state.cart_state import CartState
from ...styles import white, purple, TEXT_PURPLE


# ── % change badge ─────────────────────────────────────────────────────────────


def _pct_badge(pct) -> rx.Component:
    _up = {
        "background": "rgba(52,211,153,0.1)",
        "border": "1px solid rgba(52,211,153,0.28)",
        "border_radius": "6px",
        "color": "rgba(52,211,153,0.92)",
        "padding": "3px 9px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "12px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    _dn = {
        "background": "rgba(248,113,113,0.08)",
        "border": "1px solid rgba(248,113,113,0.25)",
        "border_radius": "6px",
        "color": "rgba(248,113,113,0.88)",
        "padding": "3px 9px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "12px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    _flat = {
        "background": white(0.04),
        "border": f"1px solid {white(0.1)}",
        "border_radius": "6px",
        "color": white(0.38),
        "padding": "3px 9px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "12px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    return rx.cond(
        pct > 0,
        rx.box(rx.icon("trending-up", size=12), rx.text(f"{pct:.2f}%"), style=_up),
        rx.cond(
            pct < 0,
            rx.box(
                rx.icon("trending-down", size=12), rx.text(f"{pct:.2f}%"), style=_dn
            ),
            rx.box(rx.icon("minus", size=11), rx.text(f"{pct:.2f}%"), style=_flat),
        ),
    )


def _price_color(pct):
    return rx.cond(
        pct > 0,
        "rgba(52,211,153,0.9)",
        rx.cond(pct < 0, "rgba(248,113,113,0.85)", white(0.55)),
    )


# ── Market cap formatter ───────────────────────────────────────────────────────


def _mktcap(mc) -> rx.Component:
    return rx.cond(
        mc >= 1_000_000_000_000,
        rx.text(
            f"{mc / 1_000_000_000_000:.1f}T",
            size="2",
            color=white(0.35),
            weight="medium",
            text_align="right",
        ),
        rx.cond(
            mc >= 1_000_000_000,
            rx.text(
                f"{mc / 1_000_000_000:.1f}B",
                size="2",
                color=white(0.35),
                weight="medium",
                text_align="right",
            ),
            rx.cond(
                mc > 0,
                rx.text(
                    f"{mc / 1_000_000:.0f}M",
                    size="2",
                    color=white(0.35),
                    weight="medium",
                    text_align="right",
                ),
                rx.text("—", size="2", color=white(0.18), text_align="right"),
            ),
        ),
    )


# ── Cart button ────────────────────────────────────────────────────────────────
# NOTE: Replace CartState.add_to_cart with the correct event from your CartState.


def _cart_btn(symbol: str) -> rx.Component:
    return rx.button(
        rx.icon("shopping-cart", size=14),
        on_click=CartState.add_item(symbol),
        style={
            "background": white(0.04),
            "border": f"1px solid {white(0.09)}",
            "border_radius": "8px",
            "color": white(0.38),
            "cursor": "pointer",
            "transition": "all 0.15s ease",
            "_hover": {
                "background": purple(0.18),
                "border_color": purple(0.45),
                "color": TEXT_PURPLE,
            },
            "width": "34px",
            "height": "34px",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "flex_shrink": "0",
            "padding": "0",
            "min_width": "auto",
        },
    )


# ── Column header ──────────────────────────────────────────────────────────────

_COL = {
    "font_size": "10px",
    "font_weight": "700",
    "color": white(0.22),
    "letter_spacing": "0.09em",
    "text_transform": "uppercase",
    "white_space": "nowrap",
}


def _header() -> rx.Component:
    return rx.hstack(
        rx.box(rx.text("Symbol", style=_COL), flex="1", min_width="240px"),
        rx.box(rx.text("Price", style={**_COL, "text_align": "right"}), width="90px"),
        rx.box(
            rx.text("% Change", style={**_COL, "text_align": "center"}), width="110px"
        ),
        rx.box(rx.text("Volume", style={**_COL, "text_align": "right"}), width="120px"),
        rx.box(rx.text("Mkt Cap", style={**_COL, "text_align": "right"}), width="90px"),
        rx.box(width="46px"),
        spacing="4",
        align="center",
        width="100%",
        padding="0.55em 1.5em",
        border_bottom=f"1px solid {white(0.07)}",
    )


# ── Single ticker row ──────────────────────────────────────────────────────────


def ticker_row(ticker: dict) -> rx.Component:
    symbol = ticker["symbol"].to(str)
    name = ticker.get("company_name", "").to(str)
    exchange = ticker.get("exchange", "").to(str)
    price = ticker.get("current_price", 0).to(float)
    pct = ticker.get("pct_price_change", 0).to(float)
    volume = ticker.get("accumulated_volume", 0).to(float)
    mktcap = ticker.get("market_cap", 0).to(float)

    return rx.box(
        rx.hstack(
            # Symbol + name + exchange badge
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(symbol, size="4", weight="bold", color="white"),
                        rx.cond(
                            exchange != "",
                            rx.badge(
                                exchange,
                                size="1",
                                style={
                                    "background": white(0.05),
                                    "border": f"1px solid {white(0.09)}",
                                    "border_radius": "4px",
                                    "color": white(0.38),
                                    "font_size": "9px",
                                    "letter_spacing": "0.05em",
                                    "padding": "1px 5px",
                                },
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        name,
                        size="1",
                        color=white(0.22),
                        style={
                            "max_width": "340px",
                            "white_space": "nowrap",
                            "overflow": "hidden",
                            "text_overflow": "ellipsis",
                        },
                    ),
                    spacing="0",
                    align="start",
                ),
                flex="1",
                min_width="240px",
            ),
            # Price
            rx.box(
                rx.text(
                    price,
                    size="3",
                    weight="bold",
                    color=_price_color(pct),
                    text_align="right",
                ),
                width="90px",
                text_align="right",
            ),
            # % change
            rx.box(
                _pct_badge(pct),
                width="110px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            # Volume
            rx.box(
                rx.text(
                    volume,
                    size="2",
                    color=white(0.42),
                    weight="medium",
                    text_align="right",
                ),
                width="120px",
                text_align="right",
            ),
            # Market cap
            rx.box(
                _mktcap(mktcap),
                width="90px",
                display="flex",
                align_items="center",
                justify_content="flex-end",
            ),
            # Cart — stops row click from propagating
            rx.box(
                _cart_btn(symbol),
                width="46px",
                display="flex",
                align_items="center",
                justify_content="center",
                on_click=rx.stop_propagation,
            ),
            spacing="4",
            align="center",
            width="100%",
            padding="0.85em 1.5em",
        ),
        on_click=rx.redirect(f"/analyze/{symbol}"),
        cursor="pointer",
        width="100%",
        style={
            "border_bottom": f"1px solid {white(0.05)}",
            "transition": "background 0.1s ease",
            "_hover": {"background": white(0.03)},
        },
    )


# ── Skeleton rows ──────────────────────────────────────────────────────────────


def _skel(w: str, h: str = "13px") -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h), loading=True, style={"border_radius": "5px"}
    )


def _skeleton_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(_skel("110px", "17px"), _skel("200px", "11px"), spacing="2"),
        rx.spacer(),
        _skel("55px"),
        _skel("80px", "26px"),
        _skel("70px"),
        _skel("50px"),
        _skel("34px", "34px"),
        spacing="4",
        align="center",
        width="100%",
        padding="0.85em 1.5em",
        border_bottom=f"1px solid {white(0.05)}",
    )


# ── Empty state ────────────────────────────────────────────────────────────────


def _empty_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("search-x", size=28, color=white(0.18)),
                padding="1.25em",
                border_radius="14px",
                background=white(0.03),
                border=f"1px solid {white(0.07)}",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text("No tickers found", size="4", weight="bold", color=white(0.45)),
            rx.text(
                "Try adjusting your search or filters.",
                size="2",
                color=white(0.25),
                text_align="center",
            ),
            spacing="3",
            align="center",
        ),
        height="18em",
    )


# ── Public export ──────────────────────────────────────────────────────────────


def new_ticker_board() -> rx.Component:
    return rx.box(
        _header(),
        rx.cond(
            TickerBoardState.get_all_tickers.length() > 0,
            rx.vstack(
                rx.foreach(TickerBoardState.get_all_tickers, ticker_row),
                spacing="0",
                width="100%",
            ),
            _empty_state(),
        ),
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
        overflow="hidden",
        width="100%",
    )
