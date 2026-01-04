"""Sort and search components for the select page - FIXED VERSION."""

import reflex as rx

from .state import State
from .filters import display_selected_filter, filter_button
from ...components.graph import pct_change_badge
from ...state import SearchBarState


def search_suggestion_card(ticker_value: dict):
    """Suggestion card for select page search - filters board and navigates."""

    ticker = ticker_value["symbol"].to(str)
    industry = ticker_value["industry"].to(str)
    pct_price_change: float = ticker_value["pct_price_change"].to(float)

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(ticker, size="5", weight="medium"),
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
        on_click=[rx.redirect(f"/analyze/{ticker}"), State.set_search_query("")],
        width="100%",
        padding="10px",
        cursor="pointer",
        _hover={"background_color": rx.color("gray", 3)},
    )


def display_sort_options() -> rx.Component:
    asc_icon: rx.Component = rx.icon("arrow-down-a-z", size=13)
    desc_icon: rx.Component = rx.icon("arrow-down-z-a", size=13)

    return rx.fragment(
        rx.menu.root(
            rx.menu.trigger(
                rx.button(
                    rx.hstack(
                        rx.cond(
                            State.selected_sort_order == "ASC", asc_icon, desc_icon
                        ),
                        rx.text("Sort"),
                        align="center",
                    ),
                    variant="outline",
                ),
            ),
            rx.menu.content(
                rx.foreach(
                    State.sort_options.keys(),
                    lambda option: rx.menu.sub(
                        rx.menu.sub_trigger(option),
                        rx.menu.sub_content(
                            rx.foreach(
                                State.sort_orders,
                                lambda order: rx.menu.item(
                                    rx.hstack(
                                        rx.cond(
                                            order == "ASC",
                                            asc_icon,
                                            desc_icon,
                                        ),
                                        rx.text(order),
                                        align="center",
                                        justify="between",
                                    ),
                                    on_click=[
                                        State.set_sort_option(option),
                                        State.set_sort_order(order),
                                    ],
                                ),
                            )
                        ),
                    ),
                )
            ),
        )
    )


def ticker_filter():
    """Filter bar with fast search that directly filters the ticker board below."""
    return rx.flex(
        rx.box(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=16)),
                placeholder="Search for a ticker",
                type="search",
                size="2",
                width="100%",
                color_scheme="violet",
                radius="large",
                value=State.search_query,
                on_change=State.set_search_query,
            ),
            width="30%",
            height="100%",
            align="center",
            marginRight="0.5em",
        ),
        # Selected filter chips
        rx.scroll_area(
            display_selected_filter(),
            scrollbars="horizontal",
            paddingTop="0.1em",
            type="hover",
            width="48em",
            height="2.6em",
        ),
        rx.spacer(),
        # Sort button
        display_sort_options(),
        # Filter button
        filter_button(),
        paddingTop="0.75em",
        paddingBottom="0.5em",
        width="100%",
        direction="row",
        spacing="2",
        height="3em",
    )
