"""Simplified metric selector and comparison controls."""

import reflex as rx

from .state import StockComparisonState
from ...state import SearchBarState
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
                rx.text(ticker, size="3", weight="medium"),
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


def metric_category_card(category: str) -> rx.Component:
    """Render a card for a metric category with checkbox to toggle all."""
    return rx.card(
        rx.vstack(
            # Category header with checkbox
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
            # Individual metrics
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


def settings_dialog() -> rx.Component:
    """Dialog component for all settings (metrics + time period + import)."""
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
                # Header
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
                                "_hover": {"color": rx.color("violet", 10)},
                            },
                        )
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                # Framework and controls
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
                rx.box(height="1.5em"),
                # Scrollable metrics section
                rx.scroll_area(
                    rx.vstack(
                        rx.box(
                            rx.foreach(
                                StockComparisonState.available_metrics_by_category.keys(),
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
                # Action buttons
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
    """Controls section with search bar and settings."""
    return rx.hstack(
        rx.spacer(),
        rx.hstack(
            comparison_search_bar(),
            rx.button(
                rx.hstack(
                    rx.cond(
                        StockComparisonState.show_graphs,
                        rx.icon("eye-off", size=16),
                        rx.icon("eye", size=16),
                    ),
                    rx.text(
                        rx.cond(
                            StockComparisonState.show_graphs,
                            "Hide Graphs",
                            "Show Graphs",
                        ),
                        size="2",
                    ),
                    spacing="2",
                ),
                on_click=StockComparisonState.toggle_graphs,
                size="2",
                variant="soft",
            ),
            settings_dialog(),
            spacing="3",
            align="center",
        ),
        spacing="3",
        align="center",
        width="100%",
        margin_bottom="2em",
    )
