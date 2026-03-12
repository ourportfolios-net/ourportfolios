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
                background="rgba(255, 255, 255, 0.05)",
                border=f"1px solid {rx.color('gray', 6)}",
                border_radius="0.5rem",
                _focus={
                    "background": "rgba(255, 255, 255, 0.08)",
                    "border_color": rx.color("accent", 8),
                },
                _hover={
                    "background": "rgba(255, 255, 255, 0.07)",
                },
            ),
            rx.cond(
                SearchBarState.display_suggestion,
                # Scrollable suggestion dropdown
                rx.fragment(
                    rx.flex(
                        rx.scroll_area(
                            rx.foreach(
                                SearchBarState.suggest_tickers,
                                lambda ticker_value: suggestion_card(
                                    value=ticker_value
                                ),
                            ),
                            scrollbars="vertical",
                            type="scroll",
                        ),
                        width="100%",
                        max_height="15.625rem",
                        overflow_y="auto",
                        z_index="100",
                        background="rgb(17, 17, 19)",
                        backdrop_filter="blur(1.5rem)",
                        position="absolute",
                        top="calc(100% + 1.25rem)",
                        border_radius="0.75rem",
                        border=f"1px solid {rx.color('gray', 5)}",
                        padding="0.5rem",
                        gap="0.25rem",
                        box_shadow="0 1rem 3rem rgba(0, 0, 0, 0.45)",
                        direction="column",
                    ),
                    as_child=True,
                ),
                rx.fragment(),
            ),
            position="relative",
            width="18rem",
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
        on_click=[rx.redirect(f"/tickers/{ticker}"), SearchBarState.set_query("")],
        width="100%",
        padding="0.625rem 0.75rem",
        border_radius="0.5rem",
        cursor="pointer",
        _hover={
            "background": "rgba(255, 255, 255, 0.06)",
        },
    )
