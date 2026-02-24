"""Compare table section for the tickers page."""

import reflex as rx

from .state import TickersPageState
from ...styles import (
    white,
    purple,
    TEXT_PURPLE,
    TEXT_ACCENT,
    TOOLTIP_CURSOR,
    TOOLTIP_CONTENT_STYLE,
    TOOLTIP_WRAPPER_STYLE,
    BTN_GHOST_XS,
    DELETE_HOVER,
)


def stock_metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    ticker = stock["symbol"].to(str)
    is_best = TickersPageState.industry_best_performers[industry][metric_key] == ticker
    return rx.hstack(
        rx.box(
            rx.text(
                stock.get(metric_key, "N/A"),
                size="2",
                weight=rx.cond(is_best, "bold", "regular"),
                color=rx.cond(is_best, "rgba(52, 211, 153, 0.9)", white(0.55)),
            ),
            width="4em",
            min_width="4em",
            text_align="center",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        rx.cond(
            TickersPageState.show_graphs,
            rx.box(
                rx.cond(
                    TickersPageState.industry_metric_data_map[industry][
                        metric_key
                    ].length()
                    > 0,
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key=ticker,
                            stroke=purple(0.8),
                            fill=purple(0.15),
                            stroke_width=1.5,
                            type_="monotone",
                        ),
                        rx.recharts.x_axis(data_key="period", hide=True),
                        rx.recharts.y_axis(hide=True),
                        rx.recharts.tooltip(
                            cursor=TOOLTIP_CURSOR,
                            content_style=TOOLTIP_CONTENT_STYLE,
                            wrapper_style=TOOLTIP_WRAPPER_STYLE,
                        ),
                        data=TickersPageState.industry_metric_data_map[industry][
                            metric_key
                        ],
                        width="100%",
                        height=52,
                        margin={"top": 2, "right": 0, "left": 0, "bottom": 2},
                    ),
                    rx.box(width="100%", height="52px"),
                ),
                width="7em",
                min_width="7em",
                overflow="visible",
            ),
            rx.fragment(),
        ),
        spacing="1",
        width=rx.cond(TickersPageState.show_graphs, "12em", "6em"),
        min_width=rx.cond(TickersPageState.show_graphs, "12em", "6em"),
        height="3.5em",
        align="center",
        border_right=f"1px solid {white(0.05)}",
        padding_x="0.4em",
    )


def compare_table() -> rx.Component:
    return rx.hstack(
        # Fixed ticker column
        rx.box(
            rx.vstack(
                # Header
                rx.box(
                    rx.text(
                        "SYMBOL",
                        style={
                            "font_size": "10px",
                            "font_weight": "700",
                            "color": white(0.25),
                            "letter_spacing": "0.08em",
                        },
                    ),
                    height="3em",
                    display="flex",
                    align_items="center",
                    padding_left="0.75em",
                    border_bottom=f"1px solid {white(0.06)}",
                ),
                # Ticker rows
                rx.box(
                    rx.foreach(
                        TickersPageState.grouped_stocks.items(),
                        lambda item: rx.vstack(
                            # Industry label
                            rx.box(
                                rx.badge(
                                    item[0],
                                    size="1",
                                    variant="soft",
                                    color_scheme="violet",
                                    radius="full",
                                ),
                                padding="0.3em 0.5em",
                                border_bottom=f"1px solid {white(0.04)}",
                            ),
                            rx.foreach(
                                item[1],
                                lambda stock: rx.box(
                                    rx.box(
                                        rx.icon(
                                            "x",
                                            size=11,
                                            style={
                                                "position": "absolute",
                                                "top": "50%",
                                                "right": "0.5em",
                                                "transform": "translateY(-50%)",
                                                "opacity": "0",
                                                "transition": "opacity 0.15s ease",
                                                "color": white(0.4),
                                                "cursor": "pointer",
                                                "_hover": {"color": DELETE_HOVER},
                                            },
                                            on_click=lambda: (
                                                TickersPageState.remove_stock_from_compare(
                                                    stock["symbol"]
                                                )
                                            ),
                                            class_name="ticker-x",
                                        ),
                                        rx.link(
                                            rx.hstack(
                                                rx.text(
                                                    stock["symbol"],
                                                    weight="bold",
                                                    size="3",
                                                    color="white",
                                                ),
                                                align="center",
                                            ),
                                            href=f"/analyze/{stock['symbol']}",
                                            text_decoration="none",
                                            _hover={"text_decoration": "none"},
                                        ),
                                        position="relative",
                                        width="100%",
                                        height="3.5em",
                                        padding_left="0.75em",
                                        padding_right="2em",
                                        display="flex",
                                        align_items="center",
                                        border_bottom=f"1px solid {white(0.05)}",
                                        style={
                                            "transition": "background 0.12s ease",
                                            "_hover": {
                                                "background": white(0.03),
                                                "& .ticker-x": {"opacity": "1"},
                                            },
                                        },
                                    ),
                                ),
                            ),
                            spacing="0",
                        ),
                    ),
                    max_height="calc(100vh - 22em)",
                    overflow_y="auto",
                    overflow_x="hidden",
                ),
                spacing="0",
                width="13em",
            ),
            width="13em",
            flex_shrink="0",
            border_right=f"1px solid {white(0.06)}",
        ),
        # Scrollable metrics area
        rx.scroll_area(
            rx.vstack(
                # Header row
                rx.hstack(
                    rx.foreach(
                        TickersPageState.selected_metrics,
                        lambda metric_key: rx.box(
                            rx.text(
                                TickersPageState.metric_labels[metric_key],
                                style={
                                    "font_size": "10px",
                                    "font_weight": "700",
                                    "color": white(0.3),
                                    "letter_spacing": "0.06em",
                                    "white_space": "nowrap",
                                    "overflow": "hidden",
                                    "text_overflow": "ellipsis",
                                },
                            ),
                            width=rx.cond(TickersPageState.show_graphs, "12em", "6em"),
                            min_width=rx.cond(
                                TickersPageState.show_graphs, "12em", "6em"
                            ),
                            height="3em",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            padding_x="0.4em",
                            border_right=f"1px solid {white(0.05)}",
                            border_bottom=f"1px solid {white(0.06)}",
                        ),
                    ),
                    spacing="0",
                    align="center",
                    style={"flex_wrap": "nowrap"},
                ),
                # Data rows
                rx.foreach(
                    TickersPageState.grouped_stocks.items(),
                    lambda item: rx.vstack(
                        # Industry spacer matching the label height
                        rx.box(
                            height="2em",
                            border_bottom=f"1px solid {white(0.04)}",
                            width="100%",
                        ),
                        rx.foreach(
                            item[1],
                            lambda stock: rx.hstack(
                                rx.foreach(
                                    TickersPageState.selected_metrics,
                                    lambda metric_key: stock_metric_cell(
                                        stock, metric_key, item[0]
                                    ),
                                ),
                                spacing="0",
                                height="3.5em",
                                align="center",
                                border_bottom=f"1px solid {white(0.05)}",
                                style={
                                    "flex_wrap": "nowrap",
                                    "transition": "background 0.12s ease",
                                    "_hover": {"background": white(0.025)},
                                },
                            ),
                        ),
                        spacing="0",
                    ),
                ),
                spacing="0",
                align="start",
                width="max-content",
            ),
            scrollbars="both",
            type="auto",
            style={"width": "100%", "max_height": "calc(100vh - 20em)"},
        ),
        spacing="0",
        align="start",
        width="100%",
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
        overflow="hidden",
    )


def empty_compare_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("bar-chart-2", size=32, color=white(0.2)),
                padding="1.25em",
                border_radius="14px",
                background=white(0.035),
                border=f"1px solid {white(0.07)}",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.vstack(
                rx.text(
                    "No tickers added yet", size="4", weight="bold", color=white(0.7)
                ),
                rx.text(
                    "Use the search bar to add tickers for comparison.",
                    size="2",
                    color=white(0.3),
                    text_align="center",
                ),
                spacing="1",
                align="center",
            ),
            spacing="4",
            align="center",
        ),
        height="24em",
        width="100%",
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
    )
