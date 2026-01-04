import reflex as rx
from typing import Any, Optional


def create_metric_chart(
    category: str,
    available_metrics: list[str],
    selected_metric: str,
    chart_data: list[dict[str, Any]],
    on_metric_change: callable,
    chart_height: int = 280,
    stroke_color: str = "#8884d8",
    stroke_width: int = 3,
):
    """
    Create a single metric chart with customizable options

    Args:
        category: The title/category name for the chart
        available_metrics: list of available metrics for the dropdown
        selected_metric: Currently selected metric
        chart_data: Data for the chart in format [{"year": "2023", "value": 100}, ...]
        on_metric_change: Callback function when metric selection changes
        chart_height: Height of the chart in pixels
        stroke_color: Color of the line chart
        stroke_width: Width of the line stroke
    """
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(category, size="4", weight="medium"),
                rx.spacer(),
                rx.select(
                    available_metrics,
                    value=selected_metric,
                    on_change=on_metric_change,
                    size="1",
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.recharts.line_chart(
                    rx.recharts.line(
                        data_key="value",
                        stroke=stroke_color,
                        stroke_width=stroke_width,
                        type_="monotone",
                        dot=False,
                    ),
                    rx.recharts.x_axis(
                        data_key="year",
                        angle=-45,
                        text_anchor="end",
                        padding={"left": 20, "right": 20},
                        tick={"fontSize": 10},
                    ),
                    rx.recharts.y_axis(
                        tick={"fontSize": 10},
                    ),
                    rx.recharts.tooltip(),
                    data=chart_data,
                    width="100%",
                    height=chart_height,
                    margin={"top": 20, "right": 30, "left": 10, "bottom": 35},
                ),
                width="100%",
                style={"overflow": "hidden"},
            ),
            spacing="3",
            align="stretch",
        ),
        width="100%",
        flex="1",
        min_width="0",
        max_width="100%",
        style={"padding": "1em", "minWidth": 0, "overflow": "hidden"},
    )


def create_placeholder_chart(
    title: str,
    placeholder_text: Optional[str] = None,
    chart_height: int = 280,
):
    """
    Create a placeholder chart when no data is available

    Args:
        title: Title for the placeholder chart
        placeholder_text: Custom placeholder text (optional)
        chart_height: Height of the placeholder area
    """
    display_text = placeholder_text or f"No data available for {title}"

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(title, size="4", weight="medium"),
                rx.spacer(),
                rx.select(
                    ["No metrics available"],
                    value="No metrics available",
                    size="1",
                    disabled=True,
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.center(
                    rx.text(display_text, size="3", color="gray"),
                    height=f"{chart_height}px",
                ),
                width="100%",
                style={
                    "overflow": "hidden",
                    "border": "2px dashed #ccc",
                    "borderRadius": "8px",
                },
            ),
            spacing="3",
            align="stretch",
        ),
        width="100%",
        flex="1",
        min_width="0",
        max_width="100%",
        style={"padding": "1em", "minWidth": 0, "overflow": "hidden"},
    )


def create_dynamic_chart(
    category: str,
    metrics_by_category,
    selected_metrics,
    chart_data_by_category,
    on_metric_change_factory,
):
    """Create a dynamic chart for a specific category"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(category, size="4", weight="medium"),
                rx.spacer(),
                rx.select(
                    metrics_by_category[category],
                    value=selected_metrics[category],
                    on_change=lambda value: on_metric_change_factory(category, value),
                    size="1",
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.recharts.line_chart(
                    rx.recharts.line(
                        data_key="value",
                        stroke_width=3,
                        type_="monotone",
                        dot=False,
                    ),
                    rx.recharts.x_axis(
                        data_key="year",
                        angle=-45,
                        text_anchor="end",
                        padding={"left": 20, "right": 20},
                        tick={"fontSize": 15},
                    ),
                    rx.recharts.y_axis(
                        tick={"fontSize": 15},
                    ),
                    rx.recharts.tooltip(),
                    data=chart_data_by_category[category],
                    width="100%",
                    height=280,
                    margin={"top": 20, "right": 30, "left": 10, "bottom": 35},
                ),
                width="100%",
                style={"overflow": "hidden"},
            ),
            spacing="3",
            align="stretch",
        ),
        width="100%",
        flex="1",
        min_width="0",
        max_width="100%",
        style={"padding": "1em", "minWidth": 0, "overflow": "hidden"},
    )
