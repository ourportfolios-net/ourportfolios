"""Metric selector and comparison controls."""

import reflex as rx

from ...state import StockComparisonState, SearchBarState


def comparison_search_bar() -> rx.Component:
    """Search bar for adding tickers to compare."""
    return rx.box(
        rx.vstack(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=16)),
                placeholder="Add tickers to compare",
                type="search",
                size="2",
                value=SearchBarState.search_query,
                on_change=SearchBarState.set_query,
                on_blur=lambda: SearchBarState.set_empty_state_display_suggestions(False),
                on_focus=lambda: SearchBarState.set_empty_state_display_suggestions(True),
                width="100%",
            ),
            rx.cond(
                SearchBarState.empty_state_display_suggestion
                & (SearchBarState.get_suggest_ticker.length() > 0),
                rx.card(
                    rx.scroll_area(
                        rx.foreach(
                            SearchBarState.get_suggest_ticker,
                            lambda ticker_value: comparison_search_suggestion(ticker_value),
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
        min_width="16em",
    )


def comparison_search_suggestion(ticker_value: dict) -> rx.Component:
    """Suggestion card for the comparison search bar."""
    ticker = ticker_value["symbol"].to(str)
    industry = ticker_value["industry"].to(str)

    return rx.box(
        rx.hstack(
            rx.vstack(
                # ticker tag
                rx.text(
                    ticker,
                    size="3",
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


def view_mode_toggle() -> rx.Component:
    """Button to toggle between table and graph view"""
    return rx.button(
        rx.hstack(
            rx.cond(
                StockComparisonState.view_mode == "table",
                rx.icon("line_chart", size=16),
                rx.icon("table", size=16),
            ),
            rx.text(
                rx.cond(
                    StockComparisonState.view_mode == "table",
                    "Show Graphs",
                    "Show Table",
                ),
                size="2",
            ),
            spacing="2",
        ),
        on_click=StockComparisonState.toggle_and_load_graphs,
        size="2",
        variant="soft",
        loading=StockComparisonState.is_loading_historical,
    )


def settings_dialog() -> rx.Component:
    """Dialog component for all settings (metrics + time period + import)"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("settings", size=16),
                variant="outline",
                size="2",
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.heading("Settings", size="5", weight="bold"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            size="2",
                        )
                    ),
                    width="100%",
                    align="center",
                ),
                # Import from Cart Button
                rx.button(
                    rx.hstack(
                        rx.icon("import", size=16),
                        rx.text("Import from Cart"),
                        spacing="2",
                    ),
                    on_click=StockComparisonState.import_and_fetch_compare,
                    size="2",
                    variant="soft",
                    width="100%",
                ),
                # Time Period Switch
                rx.divider(),
                rx.vstack(
                    rx.hstack(
                        rx.text("Time Period", size="3", weight="medium"),
                        rx.spacer(),
                        rx.hstack(
                            rx.text(
                                "Quarterly",
                                size="2",
                                color=rx.cond(
                                    StockComparisonState.time_period == "quarter",
                                    rx.color("accent", 11),
                                    rx.color("gray", 10),
                                ),
                            ),
                            rx.switch(
                                checked=StockComparisonState.time_period == "year",
                                on_change=StockComparisonState.toggle_time_period,
                                size="2",
                            ),
                            rx.text(
                                "Yearly",
                                size="2",
                                color=rx.cond(
                                    StockComparisonState.time_period == "year",
                                    rx.color("accent", 11),
                                    rx.color("gray", 10),
                                ),
                            ),
                            spacing="2",
                            align="center",
                        ),
                        width="100%",
                        align="center",
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                # Metrics Selection
                rx.divider(),
                rx.vstack(
                    rx.heading("Select Metrics", size="4"),
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                StockComparisonState.available_metrics,
                                lambda metric: rx.hstack(
                                    rx.checkbox(
                                        checked=StockComparisonState.selected_metrics.contains(
                                            metric
                                        ),
                                        on_change=lambda: StockComparisonState.toggle_metric(
                                            metric
                                        ),
                                        size="2",
                                    ),
                                    rx.text(
                                        StockComparisonState.metric_labels[metric], size="2"
                                    ),
                                    spacing="2",
                                    align="center",
                                    width="100%",
                                ),
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        height="300px",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.spacer(),
                        rx.button(
                            "Select All",
                            on_click=StockComparisonState.select_all_metrics,
                            size="1",
                            variant="soft",
                        ),
                        rx.button(
                            "Clear All",
                            on_click=StockComparisonState.clear_all_metrics,
                            size="1",
                            variant="soft",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="450px",
        ),
    )


def comparison_controls() -> rx.Component:
    """Controls section with search bar and settings"""
    return rx.hstack(
        rx.spacer(),
        # Search bar and settings on the right
        rx.hstack(
            comparison_search_bar(),
            settings_dialog(),
            spacing="3",
            align="center",
        ),
        spacing="3",
        align="center",
        width="100%",
        margin_bottom="2em",
    )
