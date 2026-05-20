"""Search bar UI component with ticker suggestions."""

from typing import Any

import reflex as rx

from ourportfolios.components.graph import pct_change_badge
from ourportfolios.state import SearchBarState
from ourportfolios.ui.primitives import search_input_with_icon
from ourportfolios.ui.tokens import (
    RADIUS_MD,
    RADIUS_XS,
    SHADOW_SEARCH,
    SPACE_XS,
)


def search_bar():
    return rx.box(
        rx.vstack(
            search_input_with_icon(
                placeholder="Search for a ticker here!",
                value=SearchBarState.search_query,
                on_change=SearchBarState.set_query,
                on_blur=SearchBarState.set_display_suggestions(False),
                on_mount=SearchBarState.set_display_suggestions(False),
                on_focus=SearchBarState.set_display_suggestions(True),
                custom_attrs={
                    "autocomplete": "off",
                    "name": "op_ticker_lookup",
                    "autocapitalize": "none",
                    "autocorrect": "off",
                    "spellcheck": "false",
                    "data-1p-ignore": "true",
                    "data-lpignore": "true",
                },
                width="100%",
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
                                    value=ticker_value,
                                ),
                            ),
                            scrollbars="vertical",
                            type="auto",
                        ),
                        width="100%",
                        max_height="15.625rem",
                        z_index="100",
                        background="rgb(17, 17, 19)",
                        position="absolute",
                        top="calc(100% + 1.25rem)",
                        border_radius=RADIUS_MD,
                        border=f"1px solid {rx.color('gray', 5)}",
                        padding=SPACE_XS,
                        gap="0.25rem",
                        box_shadow=SHADOW_SEARCH,
                        direction="column",
                    ),
                    as_child=True,
                ),
                rx.fragment(),
            ),
            position="relative",
            width="18rem",
            on_mount=SearchBarState.on_mount,
            on_unmount=SearchBarState.on_unmount,
        ),
    )


def suggestion_card(value: dict[str, Any]) -> rx.Component:
    ticker = value["symbol"].to(str)
    industry = value["industry"].to(str)
    pct_price_change: float = value["pct_price_change"].to(float)

    return rx.link(
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
            # pct badge column
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
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            justify="between",
            spacing="1",
        ),
        href=f"/tickers/{ticker}",
        on_click=SearchBarState.set_query(""),
        text_decoration="none",
        color="inherit",
        display="block",
        width="100%",
        padding="0.625rem 0.75rem",
        border_radius=RADIUS_XS,
        cursor="pointer",
        _hover={
            "background": "rgba(255, 255, 255, 0.06)",
        },
    )
