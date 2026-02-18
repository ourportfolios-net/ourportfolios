"""Add framework dialog and metrics management."""

import reflex as rx

from .state import FrameworkState
from ...components.common_dialog import common_dialog


_input_style = {
    "background": "rgba(255,255,255,0.04)",
    "border": "1px solid rgba(255,255,255,0.09)",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "_placeholder": {"color": "rgba(255,255,255,0.22)"},
    "_focus": {
        "border_color": "rgba(139,92,246,0.45)",
        "box_shadow": "0 0 0 3px rgba(139,92,246,0.08)",
        "outline": "none",
    },
}

_select_style = {
    "background": "rgba(255,255,255,0.04)",
    "border": "1px solid rgba(255,255,255,0.09)",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "cursor": "pointer",
}

_label_style = {
    "font_size": "11px",
    "font_weight": "600",
    "color": "rgba(255,255,255,0.55)",
    "letter_spacing": "0.07em",
    "text_transform": "uppercase",
}


def metric_hover_css() -> rx.Component:
    """Inject CSS for card-hover -> bridge reveal (both above and below)"""
    return rx.html(
        """<style>
        .metric-group:hover .swap-bridge,
        .metric-group:has(+ .metric-group:hover) .swap-bridge { 
            opacity: 1 !important; 
        }
        </style>"""
    )


def field(label: str, control) -> rx.Component:
    return rx.vstack(
        rx.text(label, style=_label_style),
        control,
        spacing="1",
        width="100%",
    )


def metric_item(metric, index: int):
    """Metric card - trash brightens on hover, swap bridge appears on card hover"""
    return rx.box(
        # Card row
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        metric.name,
                        size="2",
                        weight="medium",
                        color="rgba(255,255,255,0.85)",
                    ),
                    rx.text(metric.category, size="1", color="rgba(255,255,255,0.28)"),
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
                    style={
                        "color": "rgba(255,255,255,0.55)",
                        "transition": "color 0.15s ease",
                        "_hover": {"color": "rgba(236, 93, 94, 0.85)"},
                    },
                ),
                align="center",
                width="100%",
            ),
            padding="0.6em 0.75em",
            background="rgba(255,255,255,0.035)",
            border="1px solid rgba(255,255,255,0.09)",
            border_radius="0.625em",
            width="100%",
            style={
                "transition": "border-color 0.15s ease",
                "_hover": {
                    "border_color": "rgba(255,255,255,0.15)",
                    "background": "rgba(255,255,255,0.045)",
                },
            },
        ),
        # Swap bridge — much larger, overlaps heavily into both cards
        rx.cond(
            index < FrameworkState.metrics_count - 1,
            rx.box(
                rx.box(
                    rx.center(
                        rx.hstack(
                            rx.icon("arrow-up", size=10, color="rgba(255,255,255,0.7)"),
                            rx.icon(
                                "arrow-down", size=10, color="rgba(255,255,255,0.7)"
                            ),
                            spacing="0",
                        ),
                        width="100%",
                        height="100%",
                    ),
                    on_click=lambda: FrameworkState.move_metric_down(metric.name),
                    cursor="pointer",
                    style={
                        "width": "2.8em",
                        "height": "2.2em",
                        "background": "rgba(255,255,255,0.04)",
                        "border": "1px solid rgba(255,255,255,0.08)",
                        "border_radius": "0.5em",
                        "margin": "-0.6em auto",
                        "opacity": "0",
                        "transition": "all 0.15s ease",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "_hover": {
                            "background": "rgba(255,255,255,0.08)",
                            "border_color": "rgba(255,255,255,0.15)",
                        },
                    },
                    class_name="swap-bridge",
                ),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            rx.fragment(),
        ),
        width="100%",
        class_name="metric-group",
        style={
            "_hover .swap-bridge": {"opacity": "1"},
        },
    )


def add_metric_selector():
    content = rx.vstack(
        field(
            "Category",
            rx.select(
                FrameworkState.available_categories,
                value=FrameworkState.new_metric_category,
                on_change=FrameworkState.set_new_metric_category,
                size="3",
                width="100%",
                style=_select_style,
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
                width="100%",
                style=_select_style,
            ),
        ),
        rx.hstack(
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_metric_dialog,
                size="2",
                style={
                    "background": "rgba(255,255,255,0.05)",
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "border_radius": "8px",
                    "color": "rgba(255,255,255,0.5)",
                    "cursor": "pointer",
                    "flex": "1",
                    "_hover": {"background": "rgba(255,255,255,0.09)"},
                },
            ),
            rx.button(
                "Add Metric",
                on_click=FrameworkState.add_metric_to_form,
                size="2",
                disabled=FrameworkState.new_metric_name == "",
                style={
                    "background": "rgba(139,92,246,0.18)",
                    "border": "1px solid rgba(139,92,246,0.4)",
                    "border_radius": "8px",
                    "color": "#c4b5fd",
                    "font_weight": "600",
                    "cursor": "pointer",
                    "flex": "1",
                    "_hover": {"background": "rgba(139,92,246,0.28)"},
                },
            ),
            spacing="2",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )

    return common_dialog(
        content=content,
        is_open=FrameworkState.show_add_metric_dialog,
        on_close=FrameworkState.close_add_metric_dialog,
        on_open_change=FrameworkState.handle_add_metric_dialog_open,
        width="380px",
        height="auto",
        padding="1.5rem",
        title="Add Metric",
        title_size="5",
    )


def metrics_management_panel():
    return rx.vstack(
        rx.hstack(
            rx.text("METRICS", style=_label_style),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=12),
                "Add",
                on_click=FrameworkState.open_add_metric_dialog,
                size="1",
                style={
                    "background": "rgba(139,92,246,0.12)",
                    "border": "1px solid rgba(139,92,246,0.3)",
                    "border_radius": "6px",
                    "color": "#c4b5fd",
                    "font_weight": "600",
                    "cursor": "pointer",
                    "_hover": {"background": "rgba(139,92,246,0.22)"},
                },
            ),
            width="100%",
            align="center",
        ),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(
                    FrameworkState.form_metrics,
                    lambda metric, idx: metric_item(metric, idx),
                ),
                spacing="0",
                width="100%",
                gap="0",
            ),
            style={"height": "300px", "width": "100%"},
            scrollbars="vertical",
        ),
        spacing="3",
        width="100%",
        height="100%",
    )


def add_framework_dialog():
    content = rx.vstack(
        metric_hover_css(),
        rx.hstack(
            # Left: form — tight, full-width controls
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Title *", style=_label_style),
                        rx.input(
                            placeholder="Framework title",
                            value=FrameworkState.form_title,
                            on_change=FrameworkState.set_form_title,
                            size="3",
                            width="100%",
                            style=rx.cond(
                                FrameworkState.form_errors.contains("title"),
                                {
                                    **_input_style,
                                    "border": "1px solid rgba(255,80,80,0.5)",
                                    "box_shadow": "0 0 0 3px rgba(255,80,80,0.08)",
                                },
                                _input_style,
                            ),
                        ),
                        rx.cond(
                            FrameworkState.form_errors.contains("title"),
                            rx.text(
                                FrameworkState.form_errors["title"],
                                size="1",
                                color="rgba(255,100,100,0.8)",
                            ),
                            rx.fragment(),
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Author *", style=_label_style),
                        rx.input(
                            placeholder="Author name",
                            value=FrameworkState.form_author,
                            on_change=FrameworkState.set_form_author,
                            size="3",
                            width="100%",
                            style=rx.cond(
                                FrameworkState.form_errors.contains("author"),
                                {
                                    **_input_style,
                                    "border": "1px solid rgba(255,80,80,0.5)",
                                    "box_shadow": "0 0 0 3px rgba(255,80,80,0.08)",
                                },
                                _input_style,
                            ),
                        ),
                        rx.cond(
                            FrameworkState.form_errors.contains("author"),
                            rx.text(
                                FrameworkState.form_errors["author"],
                                size="1",
                                color="rgba(255,100,100,0.8)",
                            ),
                            rx.fragment(),
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Industry *", style=_label_style),
                        rx.select(
                            ["general", "bank", "financial_services"],
                            value=FrameworkState.form_industry,
                            on_change=FrameworkState.set_form_industry,
                            size="3",
                            width="100%",
                            style=_select_style,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Scope *", style=_label_style),
                        rx.select(
                            ["fundamental", "technical"],
                            value=FrameworkState.form_scope,
                            on_change=FrameworkState.set_form_scope,
                            size="3",
                            width="100%",
                            style=_select_style,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Complexity *", style=_label_style),
                        rx.select(
                            ["beginner-friendly", "complex"],
                            value=FrameworkState.form_complexity,
                            on_change=FrameworkState.set_form_complexity,
                            size="3",
                            width="100%",
                            style=_select_style,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Description", style=_label_style),
                    rx.text_area(
                        placeholder="Describe this framework's strategy and goals...",
                        value=FrameworkState.form_description,
                        on_change=FrameworkState.set_form_description,
                        size="3",
                        width="100%",
                        style={
                            **_input_style,
                            "flex": "1",
                            "min_height": "7em",
                            "resize": "none",
                        },
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
            # Vertical divider
            rx.box(
                width="1px",
                background="rgba(255,255,255,0.06)",
                align_self="stretch",
                flex_shrink="0",
            ),
            # Right: metrics
            rx.vstack(
                metrics_management_panel(),
                width="100%",
                flex="1",
            ),
            spacing="5",
            width="100%",
            align="start",
            height="100%",
            flex="1",
        ),
        # Footer — no divider line
        rx.hstack(
            rx.spacer(),
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_add_dialog,
                size="3",
                style={
                    "background": "rgba(255,255,255,0.05)",
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "border_radius": "10px",
                    "color": "rgba(255,255,255,0.5)",
                    "cursor": "pointer",
                    "_hover": {"background": "rgba(255,255,255,0.09)"},
                },
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
                style={
                    "background": "rgba(139,92,246,0.18)",
                    "border": "1px solid rgba(139,92,246,0.45)",
                    "border_radius": "10px",
                    "color": "#c4b5fd",
                    "font_weight": "600",
                    "cursor": "pointer",
                    "_hover": {"background": "rgba(139,92,246,0.28)"},
                },
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
        content=content,
        is_open=FrameworkState.show_add_dialog,
        on_close=FrameworkState.close_add_dialog,
        on_open_change=FrameworkState.handle_add_dialog_open,
        width="75vw",
        height="75vh",
        max_width="1800px",
        padding="1.5rem 2rem 2rem 2rem",
    )
