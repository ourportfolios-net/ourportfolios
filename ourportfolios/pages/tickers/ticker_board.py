"""
Ticker board — card-style rows.

Each row is a self-contained card:
  LEFT:  Large symbol + exchange badge stacked above the company name
  RIGHT: Stat blocks — Price · % Change · Volume · Mkt Cap — each as a
         labeled mini-card, plus a cart button.

No column header, no horizontal-table alignment. Clean, spacious, modern.
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
        "padding": "3px 10px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "13px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    _dn = {
        "background": "rgba(248,113,113,0.08)",
        "border": "1px solid rgba(248,113,113,0.25)",
        "border_radius": "6px",
        "color": "rgba(248,113,113,0.88)",
        "padding": "3px 10px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "13px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    _flat = {
        "background": white(0.04),
        "border": f"1px solid {white(0.09)}",
        "border_radius": "6px",
        "color": white(0.35),
        "padding": "3px 10px",
        "display": "inline-flex",
        "align_items": "center",
        "gap": "4px",
        "font_size": "13px",
        "font_weight": "700",
        "white_space": "nowrap",
    }
    return rx.cond(
        pct > 0,
        rx.box(rx.icon("trending-up", size=13), rx.text(f"{pct:.2f}%"), style=_up),
        rx.cond(
            pct < 0,
            rx.box(
                rx.icon("trending-down", size=13), rx.text(f"{pct:.2f}%"), style=_dn
            ),
            rx.box(rx.icon("minus", size=12), rx.text(f"{pct:.2f}%"), style=_flat),
        ),
    )


def _price_color(pct):
    return rx.cond(
        pct > 0,
        "rgba(52,211,153,0.9)",
        rx.cond(pct < 0, "rgba(248,113,113,0.85)", white(0.6)),
    )


# ── Labeled stat block ─────────────────────────────────────────────────────────


def _stat(label: str, value) -> rx.Component:
    """A small labeled stat — label on top, value below."""
    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": "9px",
                "font_weight": "700",
                "color": white(0.22),
                "letter_spacing": "0.09em",
                "text_transform": "uppercase",
                "white_space": "nowrap",
            },
        ),
        value,
        spacing="1",
        align="end",
    )


def _mktcap_text(mc) -> rx.Component:
    return rx.cond(
        mc >= 1_000_000_000_000,
        rx.text(
            f"{mc / 1_000_000_000_000:.1f}T",
            size="2",
            color=white(0.5),
            weight="medium",
        ),
        rx.cond(
            mc >= 1_000_000_000,
            rx.text(
                f"{mc / 1_000_000_000:.1f}B",
                size="2",
                color=white(0.5),
                weight="medium",
            ),
            rx.cond(
                mc > 0,
                rx.text(
                    f"{mc / 1_000_000:.0f}M",
                    size="2",
                    color=white(0.5),
                    weight="medium",
                ),
                rx.text("—", size="2", color=white(0.2)),
            ),
        ),
    )


# ── Cart button ────────────────────────────────────────────────────────────────


def _cart_btn(symbol: str) -> rx.Component:
    return rx.button(
        rx.icon("shopping-cart", size=15),
        on_click=CartState.add_item(symbol),
        style={
            "background": white(0.04),
            "border": f"1px solid {white(0.09)}",
            "border_radius": "9px",
            "color": white(0.35),
            "cursor": "pointer",
            "transition": "all 0.15s ease",
            "_hover": {
                "background": purple(0.18),
                "border_color": purple(0.45),
                "color": TEXT_PURPLE,
            },
            "width": "38px",
            "height": "38px",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "flex_shrink": "0",
            "padding": "0",
            "min_width": "auto",
        },
    )


# ── Single ticker row (card style) ────────────────────────────────────────────


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
            # ── LEFT: symbol identity block
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            symbol,
                            size="6",
                            weight="bold",
                            color="white",
                            line_height="1",
                        ),
                        rx.cond(
                            exchange != "",
                            rx.badge(
                                exchange,
                                size="1",
                                style={
                                    "background": white(0.05),
                                    "border": f"1px solid {white(0.09)}",
                                    "border_radius": "5px",
                                    "color": white(0.38),
                                    "font_size": "9px",
                                    "letter_spacing": "0.06em",
                                    "padding": "2px 6px",
                                    "align_self": "center",
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
                            "white_space": "nowrap",
                            "overflow": "hidden",
                            "text_overflow": "ellipsis",
                            "max_width": "380px",
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
            # ── RIGHT: stat blocks + cart
            rx.hstack(
                # Price
                _stat(
                    "Price",
                    rx.text(price, size="3", weight="bold", color=_price_color(pct)),
                ),
                # Divider
                rx.box(
                    width="1px", height="28px", background=white(0.07), flex_shrink="0"
                ),
                # % Change
                _stat("Change", _pct_badge(pct)),
                # Divider
                rx.box(
                    width="1px", height="28px", background=white(0.07), flex_shrink="0"
                ),
                # Volume
                _stat(
                    "Volume",
                    rx.text(volume, size="2", color=white(0.5), weight="medium"),
                ),
                # Divider
                rx.box(
                    width="1px", height="28px", background=white(0.07), flex_shrink="0"
                ),
                # Mkt Cap
                _stat("Mkt Cap", _mktcap_text(mktcap)),
                # Cart — stop propagation so row click doesn't fire
                rx.box(
                    _cart_btn(symbol),
                    on_click=rx.stop_propagation,
                    display="flex",
                    align_items="center",
                    margin_left="0.5em",
                ),
                spacing="5",
                align="center",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding="1em 1.5em",
        ),
        on_click=rx.redirect(f"/tickers/{symbol}"),
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
        rx.vstack(_skel("80px", "22px"), _skel("200px", "11px"), spacing="2"),
        rx.spacer(),
        rx.hstack(
            _skel("55px", "32px"),
            _skel("80px", "26px"),
            _skel("70px", "32px"),
            _skel("50px", "32px"),
            _skel("38px", "38px"),
            spacing="5",
            align="center",
        ),
        align="center",
        width="100%",
        padding="1em 1.5em",
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
        rx.cond(
            TickerBoardState.get_all_tickers.length() > 0,
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
            _empty_state(),
        ),
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
        overflow="hidden",
        width="100%",
    )
