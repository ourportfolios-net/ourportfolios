"""Metric selector and comparison controls."""

import reflex as rx

from ...state import StockComparisonState, SearchBarState
from ...state.framework_state import GlobalFrameworkState


def comparison_search_bar() -> rx.Component:
    """Search bar for adding tickers to compare."""
    return rx.box(
        rx.vstack(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=16)),
                placeholder="Add tickers to compare",
                type="search",
                size="2",
                value=SearchBarState.comparison_search_query,
                on_change=SearchBarState.set_comparison_query,
                on_blur=lambda: SearchBarState.set_empty_state_display_suggestions(
                    False
                ),
                on_focus=lambda: SearchBarState.set_empty_state_display_suggestions(
                    True
                ),
                width="100%",
            ),
            rx.cond(
                SearchBarState.empty_state_display_suggestion
                & (SearchBarState.get_comparison_suggest_ticker.length() > 0),
                rx.card(
                    rx.scroll_area(
                        rx.foreach(
                            SearchBarState.get_comparison_suggest_ticker,
                            lambda ticker_value: comparison_search_suggestion(
                                ticker_value
                            ),
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


def metric_category_card(category: str) -> rx.Component:
    """Render a card for a metric category with checkbox to toggle all"""
    return rx.card(
        rx.vstack(
            # Category header with checkbox to toggle all
            rx.hstack(
                rx.text(
                    category,
                    size="3",
                    weight="bold",
                    color=rx.color("accent", 11),
                ),
                rx.checkbox(
                    checked=StockComparisonState.category_selection_state[category],
                    on_change=lambda: StockComparisonState.toggle_category(category),
                    size="2",
                ),
                spacing="2",
                align="center",
                width="100%",
                justify="between",
            ),
            # Individual metrics in 2-3 column grid
            rx.box(
                rx.foreach(
                    StockComparisonState.available_metrics_by_category[category],
                    lambda metric: rx.hstack(
                        rx.checkbox(
                            checked=StockComparisonState.metric_selection_state[metric],
                            on_change=lambda: StockComparisonState.toggle_metric(
                                metric
                            ),
                            size="2",
                        ),
                        rx.text(
                            StockComparisonState.metric_labels[metric],
                            size="2",
                            color=rx.color("gray", 11),
                        ),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                ),
                display="grid",
                grid_template_columns=rx.cond(
                    StockComparisonState.available_metrics_by_category[
                        category
                    ].length()
                    > 3,
                    "repeat(2, 1fr)",
                    "1fr",
                ),
                gap="0.5em",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        size="2",
        width="100%",
    )


def market_cap_metric() -> rx.Component:
    """Market Cap is now part of Valuation category, no longer needed separately"""
    return rx.fragment()


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
                # Header with Settings title and close button
                rx.hstack(
                    rx.heading("Settings", size="6", weight="bold"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon(
                            "x",
                            size=20,
                            style={
                                "cursor": "pointer",
                                "color": rx.color("violet", 9),
                                "_hover": {
                                    "color": rx.color("violet", 10),
                                },
                            },
                        )
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                # Framework and Import/Time period controls
                rx.hstack(
                    rx.cond(
                        GlobalFrameworkState.has_selected_framework,
                        rx.link(
                            rx.hstack(
                                rx.icon("target", size=16),
                                rx.text(
                                    GlobalFrameworkState.framework_display_name,
                                    size="2",
                                    weight="medium",
                                ),
                                rx.icon("external-link", size=14),
                                spacing="2",
                                align="center",
                                padding="0.5em 0.75em",
                                style={
                                    "backgroundColor": rx.color("violet", 2),
                                    "border": f"1px solid {rx.color('violet', 4)}",
                                    "borderRadius": "6px",
                                    "transition": "all 0.2s ease",
                                    "_hover": {
                                        "backgroundColor": rx.color("violet", 3),
                                        "borderColor": rx.color("violet", 5),
                                    },
                                },
                            ),
                            href="/recommend",
                            underline="none",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("arrow-right", size=14),
                                "Select Framework",
                                size="2",
                                variant="soft",
                                color_scheme="violet",
                            ),
                            href="/recommend",
                            underline="none",
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon("import", size=16),
                            rx.text("Import from Cart"),
                            spacing="2",
                        ),
                        on_click=StockComparisonState.import_and_fetch_compare,
                        size="2",
                        variant="soft",
                    ),
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
                    spacing="3",
                ),
                rx.box(height="1.5em"),  # Spacer to act like divider
                # Scrollable metrics section
                rx.scroll_area(
                    rx.vstack(
                        rx.box(
                            rx.foreach(
                                StockComparisonState.visible_categories,
                                metric_category_card,
                            ),
                            display="grid",
                            grid_template_columns="repeat(3, 1fr)",
                            gap="1em",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"height": "50vh"},
                ),
                # Action buttons at bottom
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Select All",
                        on_click=StockComparisonState.select_all_metrics,
                        size="2",
                        variant="soft",
                    ),
                    rx.button(
                        "Clear All",
                        on_click=StockComparisonState.clear_all_metrics,
                        size="2",
                        variant="soft",
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="75vw",
            max_width="1800px",
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
