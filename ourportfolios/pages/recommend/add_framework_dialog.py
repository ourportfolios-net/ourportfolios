"""Add framework dialog and metrics management."""

import reflex as rx

from .state import FrameworkState
from ...components.dialog import common_dialog


def metric_item(metric: dict, index: int):
    """Component for a single metric in the list"""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(metric["name"], size="3", weight="medium"),
                rx.badge(metric["category"], size="1", variant="soft"),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.icon_button(
                    rx.icon("arrow-up", size=16),
                    size="1",
                    variant="ghost",
                    on_click=lambda: FrameworkState.move_metric_up(metric["name"]),
                    disabled=index == 0,
                ),
                rx.icon_button(
                    rx.icon("arrow-down", size=16),
                    size="1",
                    variant="ghost",
                    on_click=lambda: FrameworkState.move_metric_down(metric["name"]),
                    disabled=index >= FrameworkState.metrics_count - 1,
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=16),
                    size="1",
                    variant="ghost",
                    color_scheme="red",
                    on_click=lambda: FrameworkState.remove_metric(metric["name"]),
                ),
                spacing="1",
            ),
            align="center",
            width="100%",
            spacing="3",
        ),
        size="1",
        width="100%",
    )


def add_metric_selector():
    """Dialog for adding a new metric"""
    content = rx.vstack(
        rx.vstack(
            rx.text("Category", size="3", weight="medium"),
            rx.select(
                FrameworkState.available_categories,
                value=FrameworkState.new_metric_category,
                on_change=FrameworkState.set_new_metric_category,
                size="3",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            rx.text("Select Metric", size="3", weight="medium"),
            rx.select(
                rx.match(
                    FrameworkState.new_metric_category,
                    ("Per Share Value", FrameworkState.per_share_metrics),
                    ("Growth Rate", FrameworkState.growth_rate_metrics),
                    ("Profitability", FrameworkState.profitability_metrics),
                    ("Valuation", FrameworkState.valuation_metrics),
                    (
                        "Leverage & Liquidity",
                        FrameworkState.leverage_liquidity_metrics,
                    ),
                    ("Efficiency", FrameworkState.efficiency_metrics),
                    FrameworkState.per_share_metrics,
                ),
                placeholder="Choose a metric...",
                value=FrameworkState.new_metric_name,
                on_change=FrameworkState.set_new_metric_name,
                size="3",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
        rx.hstack(
            rx.spacer(),
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_metric_dialog,
                variant="soft",
                color_scheme="gray",
                size="2",
            ),
            rx.button(
                "Add Metric",
                on_click=FrameworkState.add_metric_to_form,
                size="2",
                disabled=FrameworkState.new_metric_name == "",
            ),
            spacing="2",
            width="100%",
            justify="end",
        ),
        spacing="4",
        width="100%",
    )
    
    return common_dialog(
        content=content,
        is_open=FrameworkState.show_add_metric_dialog,
        on_close=FrameworkState.close_add_metric_dialog,
        on_open_change=FrameworkState.handle_add_metric_dialog_open,
        width="400px",
        height="auto",
        padding="1.5rem",
        title="Add Metric",
        title_size="5",
    )


def metrics_management_panel():
    """Panel for managing framework metrics"""
    return rx.vstack(
        rx.hstack(
            rx.text("Metrics", size="4", weight="medium"),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=16),
                "Add Metric",
                on_click=FrameworkState.open_add_metric_dialog,
                size="2",
                variant="soft",
            ),
            width="100%",
            align="center",
        ),
        rx.cond(
            FrameworkState.form_metrics,
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        FrameworkState.form_metrics,
                        lambda metric, idx: metric_item(metric, idx),
                    ),
                    spacing="2",
                    width="100%",
                ),
                style={
                    "height": "300px",
                    "width": "100%",
                },
                scrollbars="vertical",
            ),
            rx.center(
                rx.text(
                    "No metrics added yet. Click 'Add Metric' to get started.",
                    size="2",
                    color="gray",
                ),
                padding="2rem",
            ),
        ),
        spacing="3",
        width="100%",
        height="100%",
    )


def add_framework_dialog():
    content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Title *", size="4", weight="medium"),
                        rx.input(
                            placeholder="Framework title",
                            value=FrameworkState.form_title,
                            on_change=FrameworkState.set_form_title,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        width="66%",
                    ),
                    rx.vstack(
                        rx.text("Author *", size="4", weight="medium"),
                        rx.input(
                            placeholder="Author name",
                            value=FrameworkState.form_author,
                            on_change=FrameworkState.set_form_author,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        width="33%",
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Industry *", size="4", weight="medium"),
                        rx.select(
                            ["general", "bank", "financial_services"],
                            value=FrameworkState.form_industry,
                            on_change=FrameworkState.set_form_industry,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        width="20%",
                    ),
                    rx.vstack(
                        rx.text("Scope *", size="4", weight="medium"),
                        rx.select(
                            ["fundamental", "technical"],
                            value=FrameworkState.form_scope,
                            on_change=FrameworkState.set_form_scope,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        width="40%",
                    ),
                    rx.vstack(
                        rx.text("Complexity *", size="4", weight="medium"),
                        rx.select(
                            ["beginner-friendly", "complex"],
                            value=FrameworkState.form_complexity,
                            on_change=FrameworkState.set_form_complexity,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        width="40%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Description", size="4", weight="medium"),
                    rx.text_area(
                        placeholder="Framework description...",
                        value=FrameworkState.form_description,
                        on_change=FrameworkState.set_form_description,
                        width="100%",
                        height="100%",
                        size="3",
                        min_height="9em",
                    ),
                    spacing="2",
                    width="100%",
                    height="100%",
                    flex="1",
                ),
                spacing="3",
                width="100%",
                height="100%",
                flex="2",
            ),
            rx.vstack(
                metrics_management_panel(),
                spacing="2",
                width="100%",
                height="100%",
                flex="1",
            ),
            spacing="5",
            width="100%",
            align="start",
            height="100%",
        ),
        rx.spacer(),
        rx.hstack(
            rx.spacer(),
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_dialog,
                variant="soft",
                color_scheme="gray",
                size="3",
            ),
            rx.button(
                "Add Framework",
                on_click=FrameworkState.submit_framework,
                size="3",
                disabled=rx.cond(
                    (FrameworkState.form_title == "")
                    | (FrameworkState.form_author == ""),
                    True,
                    False,
                ),
            ),
            spacing="2",
            width="100%",
            justify="end",
        ),
        spacing="0",
        width="100%",
        height="100%",
        justify="between",
    )
    
    return common_dialog(
        content=content,
        is_open=FrameworkState.show_add_dialog,
        on_close=FrameworkState.close_add_dialog,
        on_open_change=FrameworkState.handle_add_dialog_open,
        width="75vw",
        height="75vh",
        max_width="1800px",
        padding="1.5rem 2rem 2rem 2rem",
    )
