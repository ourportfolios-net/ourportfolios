"""Add framework dialog and metrics management."""

from collections.abc import Callable

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.styles import (
    BTN_GHOST,
    BTN_GHOST_SM,
    BTN_SECONDARY,
    DELETE_HOVER,
    ERROR_BORDER,
    ERROR_COLOR,
    ERROR_SHADOW,
    INPUT_STYLE,
    LABEL_STYLE,
    SELECT_STYLE,
    white,
)


def field(label: str, control: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, **LABEL_STYLE),
        control,
        spacing="1",
        width="100%",
    )


def metric_item(metric: object, index: int) -> rx.Component:
    # The swap bridge is visible when hovering this row (index == hovered)
    # OR hovering the row below it (index == hovered - 1).
    # FrameworkState needs:
    #   hovered_metric_index: int = -1
    #   def set_hovered_metric_index(self, i: int): self.hovered_metric_index = i
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
            border_radius="0.625em",
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
                    border_radius="0.5em",
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
        field(
            "Category",
            rx.select(
                FrameworkState.available_categories,
                value=FrameworkState.new_metric_category,
                on_change=FrameworkState.set_new_metric_category,
                size="3",
                **SELECT_STYLE,
            ),
        ),
        field(
            "Metric",
            rx.select(
                rx.match(
                    FrameworkState.new_metric_category,
                    ("Per Share Value", FrameworkState.per_share_metrics),
                    ("Growth Rate", FrameworkState.growth_rate_metrics),
                    ("Profitability", FrameworkState.profitability_metrics),
                    ("Valuation", FrameworkState.valuation_metrics),
                    ("Leverage & Liquidity", FrameworkState.leverage_liquidity_metrics),
                    ("Efficiency", FrameworkState.efficiency_metrics),
                    FrameworkState.per_share_metrics,
                ),
                placeholder="Choose a metric...",
                value=FrameworkState.new_metric_name,
                on_change=FrameworkState.set_new_metric_name,
                size="3",
                **SELECT_STYLE,
            ),
        ),
        rx.hstack(
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_metric_dialog,
                size="2",
                **BTN_GHOST,
            ),
            rx.button(
                "Add Metric",
                on_click=FrameworkState.add_metric_to_form,
                size="2",
                disabled=FrameworkState.new_metric_name == "",
                **BTN_GHOST_SM,
            ),
            spacing="2",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=FrameworkState.show_add_metric_dialog,
            on_close=FrameworkState.close_add_metric_dialog,
            on_open_change=FrameworkState.handle_add_metric_dialog_open,
            width="23.75rem",
            height="auto",
            padding="1.5rem",
            title="Add Metric",
            title_size="5",
        ),
    )


def metrics_management_panel() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("METRICS", **LABEL_STYLE),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=12),
                "Add",
                on_click=FrameworkState.open_add_metric_dialog,
                size="2",
                **BTN_SECONDARY,
            ),
            width="100%",
            align="center",
        ),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(
                    FrameworkState.form_metrics,
                    metric_item,
                ),
                spacing="0",
                width="100%",
                gap="0",
            ),
            height="18.75rem",
            width="100%",
            scrollbars="vertical",
        ),
        spacing="3",
        width="100%",
        height="100%",
    )


def _input_with_error(
    placeholder: str,
    value: str,
    on_change: Callable[..., object],
    error_key: str,
) -> rx.Component:
    return rx.vstack(
        rx.input(
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
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Title *", **LABEL_STYLE),
                        _input_with_error(
                            "Framework title",
                            FrameworkState.form_title,
                            FrameworkState.set_form_title,
                            "title",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Author *", **LABEL_STYLE),
                        _input_with_error(
                            "Author name",
                            FrameworkState.form_author,
                            FrameworkState.set_form_author,
                            "author",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Industry *", **LABEL_STYLE),
                        rx.select(
                            ["general", "bank", "financial_services"],
                            value=FrameworkState.form_industry,
                            on_change=FrameworkState.set_form_industry,
                            size="3",
                            **SELECT_STYLE,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Scope *", **LABEL_STYLE),
                        rx.select(
                            ["fundamental", "technical"],
                            value=FrameworkState.form_scope,
                            on_change=FrameworkState.set_form_scope,
                            size="3",
                            **SELECT_STYLE,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Complexity *", **LABEL_STYLE),
                        rx.select(
                            ["beginner-friendly", "complex"],
                            value=FrameworkState.form_complexity,
                            on_change=FrameworkState.set_form_complexity,
                            size="3",
                            **SELECT_STYLE,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Description", **LABEL_STYLE),
                    rx.text_area(
                        placeholder="Describe this framework's strategy and goals...",
                        value=FrameworkState.form_description,
                        on_change=FrameworkState.set_form_description,
                        size="3",
                        **INPUT_STYLE,
                        flex="1",
                        min_height="7em",
                        resize="none",
                    ),
                    spacing="1",
                    width="100%",
                    flex="1",
                ),
                spacing="3",
                width="100%",
                flex="2",
                height="100%",
            ),
            rx.box(
                width="1px",
                background=white(0.06),
                align_self="stretch",
                flex_shrink="0",
            ),
            rx.vstack(metrics_management_panel(), width="100%", flex="1"),
            spacing="5",
            width="100%",
            align="start",
            height="100%",
            flex="1",
        ),
        rx.hstack(
            rx.spacer(),
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_dialog,
                size="3",
                **BTN_GHOST,
            ),
            rx.button(
                "Add Framework",
                on_click=FrameworkState.submit_framework,
                size="3",
                disabled=(FrameworkState.form_title == "")
                | (FrameworkState.form_author == ""),
                **BTN_GHOST,
            ),
            spacing="2",
            width="100%",
            padding_top="0.75rem",
        ),
        spacing="4",
        width="100%",
        height="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=FrameworkState.show_add_dialog,
            on_close=FrameworkState.close_add_dialog,
            on_open_change=FrameworkState.handle_add_dialog_open,
            width="75vw",
            height="75vh",
            max_width="112.5rem",
            padding="1.5rem 2rem 2rem 2rem",
        ),
    )
