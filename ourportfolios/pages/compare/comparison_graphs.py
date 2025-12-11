"""Comparison graphs components for visualizing metrics over time."""

import reflex as rx

from ...state import StockComparisonState


def metric_line_graph(metric_key: str) -> rx.Component:
    """Create a line chart for a specific metric showing all stocks over time"""
    
    return rx.card(
        rx.vstack(
            # Title
            rx.hstack(
                rx.text(
                    StockComparisonState.metric_labels[metric_key],
                    size="5",
                    weight="bold",
                ),
                rx.spacer(),
                width="100%",
            ),
            # Chart - dynamically show lines based on compare list length
            rx.cond(
                StockComparisonState.get_metric_data[metric_key].length() > 0,
                rx.recharts.line_chart(
                    # Line 1
                    rx.cond(
                        StockComparisonState.compare_list_length > 0,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[0],
                            stroke="#3B9EFF",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[0],
                        ),
                    ),
                    # Line 2
                    rx.cond(
                        StockComparisonState.compare_list_length > 1,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[1],
                            stroke="#46FEA5",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[1],
                        ),
                    ),
                    # Line 3
                    rx.cond(
                        StockComparisonState.compare_list_length > 2,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[2],
                            stroke="#FF6465",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[2],
                        ),
                    ),
                    # Line 4
                    rx.cond(
                        StockComparisonState.compare_list_length > 3,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[3],
                            stroke="#FFAA33",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[3],
                        ),
                    ),
                    # Line 5
                    rx.cond(
                        StockComparisonState.compare_list_length > 4,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[4],
                            stroke="#9176FE",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[4],
                        ),
                    ),
                    # Line 6
                    rx.cond(
                        StockComparisonState.compare_list_length > 5,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[5],
                            stroke="#00E0D0",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[5],
                        ),
                    ),
                    # Line 7
                    rx.cond(
                        StockComparisonState.compare_list_length > 6,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[6],
                            stroke="#FF66B2",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[6],
                        ),
                    ),
                    # Line 8
                    rx.cond(
                        StockComparisonState.compare_list_length > 7,
                        rx.recharts.line(
                            data_key=StockComparisonState.compare_list[7],
                            stroke="#FFD60A",
                            stroke_width=2,
                            dot={"r": 4},
                            name=StockComparisonState.compare_list[7],
                        ),
                    ),
                    rx.recharts.x_axis(
                        data_key="period",
                        label={
                            "value": "Period",
                            "position": "insideBottom",
                            "offset": -5,
                        },
                    ),
                    rx.recharts.y_axis(
                        label={
                            "value": StockComparisonState.metric_labels[metric_key],
                            "angle": -90,
                            "position": "insideLeft",
                        },
                    ),
                    rx.recharts.legend(),
                    rx.recharts.tooltip(
                        cursor={"strokeDasharray": "3 3"},
                        content_style={
                            "backgroundColor": "rgba(0, 0, 0, 0.9)",
                            "border": "1px solid #666",
                            "borderRadius": "6px",
                            "padding": "10px",
                        },
                        wrapper_style={"zIndex": "1000"},
                    ),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                    data=StockComparisonState.get_metric_data[metric_key],
                    width="100%",
                    height=400,
                    style={"cursor": "crosshair"},
                ),
                rx.center(
                    rx.text(
                        "No historical data available for this metric",
                        color=rx.color("gray", 10),
                    ),
                    height="300px",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        style={"margin_bottom": "1.5em"},
    )


def comparison_graphs_section() -> rx.Component:
    """Main graphs section showing all selected metrics"""
    return rx.box(
        rx.vstack(
            rx.cond(
                StockComparisonState.selected_metrics_length > 0,
                rx.vstack(
                    rx.foreach(
                        StockComparisonState.selected_metrics,
                        lambda metric_key: metric_line_graph(metric_key),
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.text(
                        "Please select at least one metric to view graphs",
                        size="3",
                        color=rx.color("gray", 10),
                    ),
                    height="40vh",
                ),
            ),
            width="100%",
        ),
        width="100%",
        padding="1.5em",
    )
