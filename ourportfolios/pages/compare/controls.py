"""Metric selector and comparison controls."""

import reflex as rx

from ...state import StockComparisonState


def metric_selector_popover() -> rx.Component:
    """Popover component for selecting metrics to compare"""
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.hstack(rx.icon("settings", size=16), spacing="2"),
                variant="outline",
                size="2",
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.hstack(
                    rx.heading("Select metrics"),
                    rx.spacer(),
                    rx.popover.close(
                        rx.button(rx.icon("x", size=16), variant="ghost", size="1")
                    ),
                    width="100%",
                    align="center",
                ),
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
                rx.spacer(),
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
                spacing="3",
                width="300px",
                padding="0.7em",
            ),
            side="bottom",
            align="start",
        ),
    )


def comparison_controls() -> rx.Component:
    """Controls section with metric selector and load button"""
    return rx.hstack(
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("import", size=16), spacing="2"),
                on_click=StockComparisonState.import_and_fetch_compare,
                size="2",
            ),
            metric_selector_popover(),
            spacing="3",
            align="center",
        ),
        spacing="0",
        align="center",
        width="100%",
        margin_bottom="2em",
    )
