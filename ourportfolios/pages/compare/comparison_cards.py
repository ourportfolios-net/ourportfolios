"""Comparison cards and controls components."""

import reflex as rx
from typing import List, Dict, Any

from ...state import StockComparisonState


def stock_metric_cell(stock: Dict[str, Any], metric_key: str, industry: str) -> rx.Component:
    """Create a single metric cell with value and graph for one stock (horizontal layout)"""
    return rx.hstack(
        # Value
        rx.box(
            rx.text(
                stock[metric_key],
                size="2",
                weight=rx.cond(
                    StockComparisonState.industry_best_performers[industry][metric_key]
                    == stock["symbol"],
                    "medium",
                    "regular",
                ),
                color=rx.cond(
                    StockComparisonState.industry_best_performers[industry][metric_key]
                    == stock["symbol"],
                    rx.color("green", 11),
                    rx.color("gray", 11),
                ),
            ),
            width="4em",
            min_width="4em",
            text_align="center",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        # Graph
        rx.box(
            rx.cond(
                StockComparisonState.industry_metric_data_map[industry][metric_key].length() > 0,
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key=stock["symbol"],
                        stroke=rx.color("accent", 10),
                        fill=rx.color("accent", 4),
                        stroke_width=2,
                        type_="monotone",
                    ),
                    rx.recharts.x_axis(data_key="period", hide=True),
                    rx.recharts.y_axis(hide=True),
                    rx.recharts.tooltip(
                        cursor={"fill": "rgba(255, 255, 255, 0.1)"},
                        content_style={
                            "backgroundColor": "rgba(0, 0, 0, 0.8)",
                            "border": "1px solid #ccc",
                            "borderRadius": "4px",
                        },
                        wrapper_style={"zIndex": "1000"},
                    ),
                    data=StockComparisonState.industry_metric_data_map[industry][metric_key],
                    width="100%",
                    height=56,
                    margin={"top": 0, "right": 0, "left": 0, "bottom": 0},
                    style={"cursor": "crosshair"},
                ),
                rx.box(width="100%", height="56px"),
            ),
            width="7em",
            min_width="7em",
            position="relative",
            style={"pointerEvents": "auto"},
        ),
        spacing="1",
        width="auto",
        min_width="12em",
        height="3.5em",
        align="center",
        border_right=f"1px solid {rx.color('gray', 4)}",
        padding_left="0.3em",
        padding_right="0.3em",
    )


def stock_column_card(stock: Dict[str, Any], industry: str) -> rx.Component:
    """Create a column with separate header card and metrics card for each stock"""
    market_cap = stock.get("market_cap", "")
    ticker = stock.get("symbol", "")

    return rx.vstack(
        # Header card - separate from metrics
        rx.card(
            rx.box(
                rx.button(
                    rx.icon("x", size=12),
                    on_click=lambda: StockComparisonState.remove_stock_from_compare(
                        ticker
                    ),
                    variant="ghost",
                    size="2",
                    style={
                        "position": "absolute",
                        "top": "0.5em",
                        "right": "0.5em",
                        "min_width": "auto",
                        "height": "auto",
                        "opacity": "0.7",
                    },
                ),
                rx.link(
                    rx.vstack(
                        rx.text(
                            ticker,
                            weight="medium",
                            size="8",
                            color=rx.color("gray", 12),
                            letter_spacing="0.05em",
                        ),
                        rx.badge(
                            stock.get("industry", ""),
                            size="1",
                            variant="soft",
                            style={"font_size": "0.7em"},
                        ),
                        rx.text(
                            f"{market_cap} B. VND",
                            size="1",
                            color=rx.color("gray", 10),
                            weight="medium",
                        ),
                        spacing="2",
                        justify="center",
                        width="100%",
                        padding_bottom="0.2em",
                    ),
                    href=f"/analyze/{ticker}",
                    text_decoration="none",
                    _hover={
                        "text_decoration": "none",
                    },
                    width="100%",
                ),
                position="relative",
                width="100%",
            ),
            width="12em",
            style={
                "flex_shrink": "0",
                "transition": "transform 0.2s ease",
            },
            _hover={
                "transform": "translateY(-0.4em)",
            },
        ),
        # Metrics card
        rx.card(
            rx.vstack(
                rx.foreach(
                    StockComparisonState.selected_metrics,
                    lambda metric_key: rx.box(
                        rx.text(
                            stock[metric_key],
                            size="2",
                            weight=rx.cond(
                                StockComparisonState.industry_best_performers[industry][
                                    metric_key
                                ]
                                == ticker,
                                "medium",
                                "regular",
                            ),
                            color=rx.cond(
                                StockComparisonState.industry_best_performers[industry][
                                    metric_key
                                ]
                                == ticker,
                                rx.color("green", 11),
                                rx.color("gray", 11),
                            ),
                        ),
                        width="100%",
                        min_height="2.5em",
                        text_align="center",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_bottom=f"1px solid {rx.color('gray', 4)}",
                    ),
                ),
                spacing="0",
                width="100%",
            ),
            width="11.5em",
            style={"flex_shrink": "0"},
        ),
        spacing="5",
        align="center",
        width="12em",
        min_width="12em",
        style={"flex_shrink": "0"},
    )


def metric_labels_row() -> rx.Component:
    """Fixed row showing metric labels (horizontal layout)"""
    return rx.hstack(
        # Empty space for alignment with ticker cards
        rx.box(
            height="2.8em",
            width="15em",
            flex_shrink="0",
        ),
        # Metrics labels - will scroll with content
        rx.card(
            rx.hstack(
                rx.foreach(
                    StockComparisonState.selected_metrics,
                    lambda metric_key: rx.box(
                        rx.text(
                            StockComparisonState.metric_labels[metric_key],
                            size="2",
                            weight="medium",
                            color=rx.color("gray", 12),
                        ),
                        width="12em",
                        min_width="12em",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        height="100%",
                        padding_left="0.3em",
                        padding_right="0.3em",
                        border_right=f"1px solid {rx.color('gray', 4)}",
                    ),
                ),
                spacing="0",
                height="100%",
                align="center",
                style={"flex_wrap": "nowrap"},
            ),
            height="2.8em",
            style={"flex_shrink": "0"},
        ),
        spacing="3",
        align="start",
        style={"flex_shrink": "0", "overflow": "hidden"},
    )


# industry_group_section is no longer used - logic moved to index.py for unified scrolling
