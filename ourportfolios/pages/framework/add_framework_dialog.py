from collections.abc import Callable
from typing import cast

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.framework.state import FrameworkState, MetricModel
from ourportfolios.ui.primitives import (
    ghost_button,
    ghost_button_sm,
    label_text,
    select_input,
    text_area_input,
    text_input,
)
from ourportfolios.ui.theme import (
    BUTTON_SECONDARY,
    DELETE_HOVER,
    ERROR_BORDER,
    ERROR_COLOR,
    ERROR_SHADOW,
    INPUT_STYLE,
    white,
)
from ourportfolios.ui.theme.surfaces import RADIUS_BUTTON, RADIUS_INPUT

# Character limit for ~500 words
DESC_CHAR_LIMIT = 3000


def field(label: str, control: rx.Component) -> rx.Component:
    return rx.vstack(
        label_text(label),
        control,
        spacing="1",
        width="100%",
    )


def metric_item(metric: MetricModel, index: int) -> rx.Component:
    bridge_visible = (FrameworkState.hovered_metric_index == index) | (
        FrameworkState.hovered_metric_index == index + 1
    )

    return rx.box(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(metric.name, size="2", weight="medium", color=white(0.85)),
                    rx.text(metric.category, size="1", color=white(0.28)),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.box(
                    rx.icon("trash-2", size=14),
                    on_click=lambda: FrameworkState.remove_metric(metric.name),
                    cursor="pointer",
                    display="flex",
                    align_items="center",
                    color=white(0.55),
                    transition="color 0.15s ease",
                    _hover={"color": DELETE_HOVER},
                ),
                align="center",
                width="100%",
            ),
            padding="0.6em 0.75em",
            background=white(0.035),
            border=f"1px solid {white(0.09)}",
            border_radius=RADIUS_INPUT,
            width="100%",
            transition="border-color 0.15s ease",
            _hover={
                "border_color": white(0.15),
                "background": white(0.045),
            },
        ),
        rx.cond(
            index < FrameworkState.metrics_count - 1,
            rx.box(
                rx.box(
                    rx.center(
                        rx.hstack(
                            rx.icon("arrow-up", size=10, color=white(0.7)),
                            rx.icon("arrow-down", size=10, color=white(0.7)),
                            spacing="0",
                        ),
                        width="100%",
                        height="100%",
                    ),
                    on_click=lambda: FrameworkState.move_metric_down(metric.name),
                    cursor="pointer",
                    width="2.8em",
                    height="2.2em",
                    background=white(0.04),
                    border=f"1px solid {white(0.08)}",
                    border_radius=RADIUS_BUTTON,
                    margin="-0.6em auto",
                    transition="opacity 0.15s ease",
                    opacity=rx.cond(bridge_visible, "1", "0"),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    _hover={
                        "background": white(0.08),
                        "border_color": white(0.15),
                    },
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            rx.fragment(),
        ),
        width="100%",
        on_mouse_enter=FrameworkState.set_hovered_metric_index(index),
        on_mouse_leave=FrameworkState.set_hovered_metric_index(-1),
    )


def add_metric_selector() -> rx.Component:
    content = rx.vstack(
        rx.vstack(
            field(
                "Category",
                select_input(
                    items=FrameworkState.available_categories,
                    value=FrameworkState.new_metric_category,
                    on_change=FrameworkState.set_new_metric_category,
                    size="3",
                    width="100%",
                ),
            ),
            field(
                "Metric",
                select_input(
                    items=rx.match(
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
            ),
            spacing="4",
            width="100%",
        ),
        rx.hstack(
            rx.spacer(),
            ghost_button(
                "Cancel",
                on_click=FrameworkState.close_add_metric_dialog,
                size="3",
            ),
            ghost_button_sm(
                "Add Metric",
                on_click=FrameworkState.add_metric_to_form,
                disabled=FrameworkState.new_metric_name == "",
            ),
            spacing="3",
            width="100%",
            padding_top="1rem",
            border_top=f"1px solid {white(0.06)}",
        ),
        spacing="5",
        width="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=cast("bool", FrameworkState.show_add_metric_dialog),
            on_close=FrameworkState.close_add_metric_dialog,
            on_open_change=FrameworkState.handle_add_metric_dialog_open,
            width="28rem",
            height="auto",
            title="Add Metric",
            title_size="5",
        ),
    )


def metrics_management_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            label_text("METRICS"),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=12),
                "Add",
                on_click=FrameworkState.open_add_metric_dialog,
                size="2",
                style=BUTTON_SECONDARY,
            ),
            width="100%",
            align="center",
        ),
        rx.vstack(
            rx.foreach(
                FrameworkState.form_metrics,
                metric_item,
            ),
            spacing="0",
            width="100%",
            gap="0",
        ),
        spacing="3",
        width="100%",
    )


def _input_with_error(
    placeholder: str,
    value: rx.Var[str] | str,
    on_change: Callable[..., object],
    error_key: str,
) -> rx.Component:
    return rx.vstack(
        text_input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            size="3",
            style=rx.cond(
                FrameworkState.form_errors.contains(error_key),
                {**INPUT_STYLE, "border": ERROR_BORDER, "box_shadow": ERROR_SHADOW},
                INPUT_STYLE,
            ),
        ),
        rx.cond(
            FrameworkState.form_errors.contains(error_key),
            rx.text(FrameworkState.form_errors[error_key], size="1", color=ERROR_COLOR),
            rx.fragment(),
        ),
        spacing="1",
        width="100%",
    )


def add_framework_dialog() -> rx.Component:
    content = rx.vstack(
        rx.scroll_area(
            rx.flex(
                rx.vstack(
                    rx.flex(
                        field(
                            "Title *",
                            _input_with_error(
                                "Framework title",
                                FrameworkState.form_title,
                                FrameworkState.set_form_title,
                                "title",
                            ),
                        ),
                        field(
                            "Author *",
                            _input_with_error(
                                "Author name",
                                FrameworkState.form_author,
                                FrameworkState.set_form_author,
                                "author",
                            ),
                        ),
                        spacing="4",
                        width="100%",
                        flex_direction=["column", "row", "row"],
                    ),
                    rx.flex(
                        field(
                            "Industry *",
                            select_input(
                                items=["general", "bank", "financial_services"],
                                value=FrameworkState.form_industry,
                                on_change=FrameworkState.set_form_industry,
                                size="3",
                            ),
                        ),
                        field(
                            "Scope *",
                            select_input(
                                items=["fundamental", "technical"],
                                value=FrameworkState.form_scope,
                                on_change=FrameworkState.set_form_scope,
                                size="3",
                            ),
                        ),
                        field(
                            "Complexity *",
                            select_input(
                                items=["beginner-friendly", "complex"],
                                value=FrameworkState.form_complexity,
                                on_change=FrameworkState.set_form_complexity,
                                size="3",
                            ),
                        ),
                        gap="1rem",
                        width="100%",
                        flex_direction=["column", "row", "row"],
                    ),
                    rx.vstack(
                        rx.hstack(
                            label_text("Description"),
                            rx.spacer(),
                            rx.text(
                                f"{FrameworkState.form_description.length()} / {DESC_CHAR_LIMIT}",
                                size="1",
                                color=white(0.3),
                            ),
                            width="100%",
                        ),
                        text_area_input(
                            placeholder="Describe this framework's strategy and goals...",
                            value=FrameworkState.form_description,
                            on_change=FrameworkState.set_form_description,
                            size="3",
                            max_length=DESC_CHAR_LIMIT,
                            min_height="12rem",
                            resize="vertical",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="5",
                    width="100%",
                    flex="1.5",
                ),
                rx.box(
                    width=["100%", "1px", "1px"],
                    height=["1px", "auto", "auto"],
                    background=white(0.06),
                    align_self="stretch",
                    flex_shrink="0",
                ),
                rx.vstack(
                    metrics_management_panel(),
                    width="100%",
                    flex="1",
                    min_width=["100%", "20rem", "20rem"],
                ),
                flex_direction=["column", "row", "row"],
                gap=["2.5rem", "2.5rem", "3rem"],
                width="100%",
                align="start",
                padding_right="0.5rem",
            ),
            type="hover",
            flex="1",
            width="100%",
            scrollbars="vertical",
        ),
        rx.hstack(
            rx.spacer(),
            ghost_button(
                "Cancel",
                on_click=FrameworkState.close_add_dialog,
                size="3",
            ),
            ghost_button(
                "Add Framework",
                on_click=FrameworkState.submit_framework,
                size="3",
                disabled=(FrameworkState.form_title == "")
                | (FrameworkState.form_author == ""),
            ),
            spacing="3",
            width="100%",
            padding_top="1.25rem",
            border_top=f"1px solid {white(0.06)}",
        ),
        spacing="0",
        width="100%",
        height="100%",
        overflow="hidden",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=cast("bool", FrameworkState.show_add_dialog),
            on_close=FrameworkState.close_add_dialog,
            on_open_change=FrameworkState.handle_add_dialog_open,
            width="95vw",
            height="75vh",
            max_width="72rem",
        ),
    )
