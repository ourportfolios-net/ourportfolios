"""Comparison cards and controls components."""

import reflex as rx
from typing import List, Dict, Any

from ...state import StockComparisonState


def stock_metric_cell(stock: Dict[str, Any], metric_key: str, industry: str) -> rx.Component:
    """Create a single metric cell with value and graph for one stock"""
    return rx.vstack(
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
            width="100%",
            text_align="center",
            padding_top="0.5em",
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
                    rx.recharts.tooltip(),
                    data=StockComparisonState.industry_metric_data_map[industry][metric_key],
                    width="100%",
                    height=55,
                    margin={"top": 0, "right": 0, "left": 0, "bottom": 0},
                ),
                rx.box(height="55px"),
            ),
            width="100%",
            padding_top="0.3em",
            padding_bottom="0.5em",
        ),
        spacing="0",
        width="100%",
        border_bottom=f"1px solid {rx.color('gray', 4)}",
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


def metric_labels_column() -> rx.Component:
    """Fixed column showing metric labels"""
    return rx.vstack(
        rx.card(
            rx.box(
                width="12em",
                min_width="12em",
                min_height="7.5em",
            ),
            width="12em",
            min_width="12em",
            style={
                "flex_shrink": "0",
                "visibility": "hidden",
            },
        ),
        # Metrics labels card with graph space
        rx.card(
            rx.vstack(
                rx.foreach(
                    StockComparisonState.selected_metrics,
                    lambda metric_key: rx.vstack(
                        # Label
                        rx.box(
                            rx.text(
                                StockComparisonState.metric_labels[metric_key],
                                size="2",
                                weight="medium",
                                color=rx.color("gray", 12),
                            ),
                            width="100%",
                            min_height="2.5em",
                            display="flex",
                            align_items="center",
                            justify_content="start",
                        ),
                        # Graph space
                        rx.box(
                            height="80px",
                            width="100%",
                        ),
                        spacing="0",
                        width="100%",
                        border_bottom=f"1px solid {rx.color('gray', 4)}",
                    ),
                ),
                spacing="0",
                width="100%",
            ),
            width="12em",
            min_width="12em",
            style={"flex_shrink": "0"},
        ),
        spacing="2",
        align="start",
        style={"flex_shrink": "0"},
    )


def industry_group_section(industry: str, stocks: List[Dict[str, Any]]) -> rx.Component:
    """Create a section for each industry group with inline graphs"""
    return rx.vstack(
        # Stock headers
        rx.hstack(
            rx.foreach(
                stocks,
                lambda stock: rx.card(
                    rx.box(
                        rx.button(
                            rx.icon("x", size=12),
                            on_click=lambda: StockComparisonState.remove_stock_from_compare(
                                stock["symbol"]
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
                                    stock["symbol"],
                                    weight="medium",
                                    size="6",
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
                                    f"{stock.get('market_cap', '')} B. VND",
                                    size="1",
                                    color=rx.color("gray", 10),
                                    weight="medium",
                                ),
                                spacing="2",
                                justify="center",
                                width="100%",
                                padding_bottom="0.2em",
                            ),
                            href=f"/analyze/{stock['symbol']}",
                            text_decoration="none",
                            _hover={"text_decoration": "none"},
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
                    _hover={"transform": "translateY(-0.4em)"},
                ),
            ),
            spacing="3",
            style={"flex_wrap": "nowrap"},
        ),
        # Metrics cards - one per stock to align with headers
        rx.hstack(
            rx.foreach(
                stocks,
                lambda stock: rx.card(
                    rx.vstack(
                        rx.foreach(
                            StockComparisonState.selected_metrics,
                            lambda metric_key: stock_metric_cell(stock, metric_key, industry),
                        ),
                        spacing="0",
                        width="100%",
                    ),
                    width="12em",
                    style={"flex_shrink": "0"},
                ),
            ),
            spacing="3",
            style={"flex_wrap": "nowrap"},
        ),
        spacing="3",
        align="start",
        style={"flex_wrap": "nowrap"},
    )
