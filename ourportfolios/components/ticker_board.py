"""Ticker board UI component for displaying filtered ticker lists."""

import reflex as rx
from ..state import TickerBoardState, CartState
from ..components.graph import pct_change_badge


def ticker_board():
    # Predefine card layout, use for both ticker info card's header and content
    card_layout = {
        "layout_spacing": {
            "paddingRight": "2em",
            "paddingLeft": "1.3em",
            "marginTop": "0.25em",
            "marginBottom": "0.5em",
        },
        "layout_segments": {
            "symbol": {"width": "52%", "align": "left"},
            "instrument": {"width": "10%", "align": "center"},
            "cart": {"width": "12%", "align": "center"},
        },
    }

    return (
        rx.card(
            # Header
            ticker_basic_info_header(**card_layout),
            # Ticker
            rx.scroll_area(
                rx.foreach(
                    TickerBoardState.get_all_tickers,
                    lambda value: ticker_card(
                        ticker=value.symbol,
                        organ_name=value.company_name,
                        current_price=value.current_price,
                        accumulated_volume=value.accumulated_volume,
                        pct_price_change=value.pct_price_change,
                        **card_layout,
                    ),
                ),
                paddingRight="0.6em",
                type="hover",
                scrollbars="vertical",
                width="61em",
                height="80vh",
            ),
            background_color=rx.color("gray", 1),
            border_radius=6,
            width="100%",
        ),
    )


def ticker_card(
    ticker: str,
    organ_name: str,
    current_price: float,
    accumulated_volume: int,
    pct_price_change: float,
    **kwargs,
):
    color = rx.cond(
        pct_price_change.to(int) > 0,
        rx.color("green", 11),
        rx.cond(pct_price_change.to(int) < 0, rx.color("red", 9), rx.color("gray", 7)),
    )
    instrument_text_props = {"weight": "regular", "size": "3", "color": color}
    return rx.card(
        rx.flex(
            # Ticker and organ_name
            rx.box(
                rx.link(
                    rx.text(ticker, weight="medium", size="7"),
                    href=f"/analyze/{ticker}",
                    style={"textDecoration": "none", "color": "inherit"},
                ),
                rx.text(organ_name, color=rx.color("gray", 7), size="2"),
                **kwargs["layout_segments"]["symbol"],
            ),
            # Price
            rx.spacer(),
            rx.text(
                current_price,
                **instrument_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            # Volume
            rx.text(
                f"{accumulated_volume:,.3f}",
                **instrument_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            # Change
            rx.text(
                pct_change_badge(diff=pct_price_change),
                **instrument_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            # Cart button
            rx.spacer(),
            rx.button(
                rx.icon("shopping-cart", size=16),
                size="2",
                variant="soft",
                on_click=lambda: CartState.add_item(ticker),
            ),
            align="center",
            direction="row",
            width="100%",
        ),
        width="100%",
        **kwargs["layout_spacing"],
    )


def ticker_basic_info_header(**kwargs) -> rx.Component:
    heading_text_props = {
        "weight": "medium",
        "color": "white",
        "size": "3",
    }
    return rx.card(
        rx.flex(
            rx.heading(
                "Symbol",
                **heading_text_props,
                **kwargs["layout_segments"]["symbol"],
            ),
            # Price
            rx.box(width="3.7em"),  # TODO: Find a way to dynamically add this
            rx.heading(
                "Price",
                **heading_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            # Volume
            rx.heading(
                "Volume",
                **heading_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            # % Change
            rx.heading(
                "% Change",
                **heading_text_props,
                **kwargs["layout_segments"]["instrument"],
            ),
            direction="row",
            width="100%",
            **kwargs["layout_spacing"],
        ),
        variant="ghost",
    )
