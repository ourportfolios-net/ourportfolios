import reflex as rx
from ourportfolios.state.comparison_state import StockComparisonState
from ourportfolios.pages.compare.controls import comparison_controls


def stock_metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    """Single metric cell with value and optional inline sparkline graph."""
    ticker = stock["symbol"].to(str)

    return rx.hstack(
        # Value
        rx.box(
            rx.text(
                stock.get(metric_key, "N/A"),
                size="2",
                weight=rx.cond(
                    StockComparisonState.industry_best_performers[industry][metric_key]
                    == ticker,
                    "medium",
                    "regular",
                ),
                color=rx.cond(
                    StockComparisonState.industry_best_performers[industry][metric_key]
                    == ticker,
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
        # Inline sparkline graph (conditional)
        rx.cond(
            StockComparisonState.show_graphs,
            rx.box(
                rx.cond(
                    StockComparisonState.industry_metric_data_map[industry][
                        metric_key
                    ].length()
                    > 0,
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key=ticker,
                            stroke=rx.color("violet", 9),
                            fill=rx.color("violet", 3),
                            stroke_width=2,
                            type_="monotone",
                        ),
                        rx.recharts.x_axis(data_key="period", hide=True),
                        rx.recharts.y_axis(hide=True),
                        rx.recharts.tooltip(
                            cursor={"fill": "rgba(255, 255, 255, 0.1)"},
                            content_style={
                                "backgroundColor": "rgba(0, 0, 0, 0.9)",
                                "border": "1px solid #666",
                                "borderRadius": "4px",
                                "padding": "6px 10px",
                            },
                            wrapper_style={"zIndex": "1000"},
                        ),
                        data=StockComparisonState.industry_metric_data_map[industry][
                            metric_key
                        ],
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
            ),
            rx.fragment(),
        ),
        spacing="1",
        width=rx.cond(
            StockComparisonState.show_graphs,
            "12em",
            "4em",
        ),
        min_width=rx.cond(
            StockComparisonState.show_graphs,
            "12em",
            "4em",
        ),
        height="3.5em",
        align="center",
        border_right=f"1px solid {rx.color('gray', 4)}",
        padding_left="0.3em",
        padding_right="0.3em",
    )


def comparison_table_section() -> rx.Component:
    """Table view of comparison data."""
    return rx.hstack(
        # Fixed ticker symbols column
        rx.box(
            rx.vstack(
                # Empty space for metric labels header
                rx.box(height="3.5em", width="15em"),
                # Scrollable stocks area
                rx.box(
                    rx.foreach(
                        StockComparisonState.grouped_stocks.items(),
                        lambda item: rx.vstack(
                            rx.foreach(
                                item[1],
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
                                            rx.hstack(
                                                rx.text(
                                                    stock["symbol"],
                                                    weight="medium",
                                                    size="5",
                                                    color=rx.color("gray", 12),
                                                    letter_spacing="0.05em",
                                                ),
                                                rx.badge(
                                                    stock.get("industry", ""),
                                                    size="1",
                                                    variant="soft",
                                                    style={"font_size": "0.65em"},
                                                ),
                                                spacing="2",
                                                align="center",
                                                width="100%",
                                            ),
                                            href=f"/analyze/{stock['symbol']}",
                                            text_decoration="none",
                                            _hover={"text_decoration": "none"},
                                            width="100%",
                                            display="flex",
                                            align_items="center",
                                            height="100%",
                                        ),
                                        position="relative",
                                        width="100%",
                                        height="100%",
                                        display="flex",
                                        align_items="center",
                                    ),
                                    width="15em",
                                    height="3.5em",
                                    flex_shrink="0",
                                    style={
                                        "transition": "all 0.2s ease",
                                        "marginLeft": "0.6em",
                                    },
                                    _hover={"marginLeft": "0"},
                                ),
                            ),
                            spacing="2",
                            margin_bottom="1.5em",
                        ),
                    ),
                    max_height="calc(100vh - 12.8em)",
                    overflow_y="auto",
                    overflow_x="hidden",
                ),
                spacing="0",
                width="15em",
            ),
            width="15em",
            flex_shrink="0",
        ),
        # Scrollable metrics area
        rx.scroll_area(
            rx.vstack(
                # Metric labels header
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
                                width=rx.cond(
                                    StockComparisonState.show_graphs,
                                    "12em",
                                    "4em",
                                ),
                                min_width=rx.cond(
                                    StockComparisonState.show_graphs,
                                    "12em",
                                    "4em",
                                ),
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
                    height="3.5em",
                    style={"flex_shrink": "0"},
                ),
                # All stocks with metrics
                rx.foreach(
                    StockComparisonState.grouped_stocks.items(),
                    lambda item: rx.vstack(
                        rx.foreach(
                            item[1],
                            lambda stock: rx.card(
                                rx.hstack(
                                    rx.foreach(
                                        StockComparisonState.selected_metrics,
                                        lambda metric_key: stock_metric_cell(
                                            stock, metric_key, item[0]
                                        ),
                                    ),
                                    spacing="0",
                                    style={"flex_wrap": "nowrap"},
                                ),
                                height="3.5em",
                                style={"flex_shrink": "0"},
                            ),
                        ),
                        spacing="2",
                        margin_bottom="1.5em",
                    ),
                ),
                spacing="0",
                align="start",
            ),
            scrollbars="both",
            type="auto",
            style={
                "width": "100%",
                "max_height": "calc(100vh - 10em)",
            },
        ),
        spacing="5",
        align="start",
        width="100%",
        overflow="visible",
    )


def comparison_section() -> rx.Component:
    """Main comparison section."""
    return rx.box(
        rx.vstack(
            comparison_controls(),
            comparison_table_section(),
            spacing="0",
            width="100%",
        ),
        width="100%",
        style={
            "max_width": "100vw",
            "margin": "0 auto",
            "padding_top": "1.5em",
            "padding_left": "1.5em",
            "padding_right": "1.5em",
        },
    )
