"""Search bar UI component with ticker suggestions."""

import reflex as rx
from typing import Any
from .graph import pct_change_badge
from ..state import SearchBarState


def search_bar():
    return rx.box(
        rx.vstack(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=16)),
                placeholder="Search for a ticker here!",
                type="search",
                size="2",
                value=SearchBarState.search_query,
                on_change=SearchBarState.set_query,
                on_blur=SearchBarState.set_display_suggestions(False),
                on_mount=SearchBarState.set_display_suggestions(False),
                on_focus=SearchBarState.set_display_suggestions(True),
                width="100%",
            ),
            rx.cond(
                SearchBarState.display_suggestion,
                # Scrollable suggestion dropdown
                rx.fragment(
                    rx.flex(
                        rx.scroll_area(
                            rx.foreach(
                                SearchBarState.get_suggest_ticker,
                                lambda ticker_value: suggestion_card(
                                    value=ticker_value
                                ),
                            ),
                            scrollbars="vertical",
                            type="scroll",
                        ),
                        width="100%",
                        max_height=250,
                        overflow_y="auto",
                        z_index="100",
                        background_color=rx.color("gray", 2),
                        position="absolute",
                        top="calc(100% + 5px)",
                        border_radius=4,
                        direction="column",
                    ),
                    as_child=True,
                ),
                rx.fragment(),
            ),
            position="relative",
            width="20vw",
            on_mount=SearchBarState.load_state,
        ),
    )


def suggestion_card(value: dict[str, Any]) -> rx.Component:
    ticker = value["symbol"].to(str)
    industry = value["industry"].to(str)
    pct_price_change: float = value["pct_price_change"].to(float)

    return rx.box(
        rx.hstack(
            rx.vstack(
                # ticker tag
                rx.text(
                    ticker,
                    size="5",
                    weight="medium",
                ),
                # industry tag
                rx.badge(
                    industry,
                    size="2",
                    weight="regular",
                    variant="surface",
                    color_scheme="violet",
                    radius="medium",
                ),
                spacing="1",
            ),
            rx.spacer(),
            # pct badge
            rx.flex(
                rx.cond(
                    SearchBarState.outstanding_tickers.get(ticker, None),
                    rx.icon("flame", size=20, color=rx.color("tomato", 9)),
                    rx.fragment(),
                ),
                pct_change_badge(diff=pct_price_change),
                align="end",
                direction="column",
                spacing="3",
            ),
            align="center",
            spacing="1",
        ),
        on_click=[rx.redirect(f"/analyze/{ticker}"), SearchBarState.set_query("")],
        width="100%",
        padding="10px",
        cursor="pointer",
        _hover={"background_color": rx.color("gray", 3)},
    )
