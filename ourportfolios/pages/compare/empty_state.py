"""Empty state component for the comparison page with search functionality."""

import reflex as rx
from ...state import StockComparisonState, SearchBarState


def empty_state_search_suggestion(ticker_value: dict) -> rx.Component:
    """Suggestion card for the empty state search bar."""
    ticker = ticker_value["symbol"].to(str)
    industry = ticker_value["industry"].to(str)

    return rx.box(
        rx.hstack(
            rx.vstack(
                # ticker tag
                rx.text(
                    ticker,
                    size="4",
                    weight="medium",
                ),
                # industry tag
                rx.badge(
                    industry,
                    size="1",
                    weight="regular",
                    variant="surface",
                    color_scheme="violet",
                    radius="medium",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # Add button
            rx.button(
                rx.icon("plus", size=16),
                on_click=StockComparisonState.add_ticker_to_compare(ticker),
                size="2",
                variant="soft",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="0.625em",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
        _hover={"background_color": rx.color("gray", 3)},
    )


def empty_state_search_bar() -> rx.Component:
    """Search bar for adding tickers when compare list is empty."""
    return rx.box(
        rx.vstack(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=18)),
                placeholder="Add tickers to compare",
                type="search",
                size="3",
                value=SearchBarState.search_query,
                on_change=SearchBarState.set_query,
                on_blur=lambda: SearchBarState.set_empty_state_display_suggestions(False),
                on_focus=lambda: SearchBarState.set_empty_state_display_suggestions(True),
                on_mount=SearchBarState.load_state,
                width="100%",
            ),
            rx.cond(
                SearchBarState.empty_state_display_suggestion
                & (SearchBarState.get_suggest_ticker.length() > 0),
                rx.card(
                    rx.scroll_area(
                        rx.foreach(
                            SearchBarState.get_suggest_ticker,
                            empty_state_search_suggestion,
                        ),
                        scrollbars="vertical",
                        type="scroll",
                        style={"maxHeight": "18.75em"},
                    ),
                    width="100%",
                    position="absolute",
                    top="calc(100% + 0.5em)",
                    z_index="100",
                    padding="0",
                ),
                rx.fragment(),
            ),
            position="relative",
            width="100%",
        ),
        width="100%",
        max_width="19.3em",
    )


def comparison_empty_state() -> rx.Component:
    """Empty state shown when cart is empty or no tickers are selected."""
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.icon("trending_up", size=48, color=rx.color("accent", 9)),
                rx.heading(
                    "Compare stocks with beautiful charts",
                    size="8",
                    weight="bold",
                    color=rx.color("gray", 12),
                ),
                spacing="3",
                align="center",
            ),
            rx.text(
                "Detailed comparison graphs. Side-by-side metrics. All with just one search.",
                size="4",
                color=rx.color("gray", 11),
                align="center",
                max_width="37.5em",
                weight="medium",
            ),
            rx.box(height="1em"),
            # Search bar to add tickers
            empty_state_search_bar(),
            # Alternative actions
            rx.hstack(
                rx.button(
                    rx.hstack(
                        rx.icon("shopping_cart", size=16),
                        rx.text("Import from Cart"),
                        spacing="2",
                    ),
                    on_click=StockComparisonState.import_and_fetch_compare,
                    size="2",
                    variant="outline",
                ),
                rx.link(
                    rx.button(
                        rx.hstack(
                            rx.icon("list", size=16),
                            rx.text("Browse Stocks"),
                            spacing="2",
                        ),
                        size="2",
                        variant="soft",
                    ),
                    href="/select",
                    text_decoration="none",
                ),
                spacing="3",
                justify="center",
            ),
            spacing="4",
            align="center",
            padding="3em",
        ),
        min_height="70vh",
        width="100%",
    )
