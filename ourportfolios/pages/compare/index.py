"""Simplified stock comparison page - compare multiple stocks side by side."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.loading import loading_screen
from ...state import StockComparisonState

from .controls import comparison_controls


def stock_metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    """Single metric cell with highlighting for best performer."""
    ticker = stock["symbol"].to(str)

    return rx.box(
        rx.text(
            stock.get(metric_key, "N/A"),
            size="2",
            weight="medium",
            color=rx.cond(
                StockComparisonState.industry_best_performers[industry][metric_key]
                == ticker,
                rx.color("green", 11),
                rx.color("gray", 11),
            ),
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
        style={
            "background_color": rx.cond(
                StockComparisonState.industry_best_performers[industry][metric_key]
                == ticker,
                rx.color("green", 2),
                "transparent",
            ),
        },
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


def loading_skeleton() -> rx.Component:
    """Loading skeleton while data is being fetched."""
    return rx.vstack(
        rx.skeleton(height="3em", width="100%"),
        rx.skeleton(height="20em", width="100%"),
        spacing="4",
        width="100%",
    )


def empty_state() -> rx.Component:
    """Empty state when no stocks are selected."""
    return rx.center(
        rx.vstack(
            rx.icon("inbox", size=48, color=rx.color("gray", 8)),
            rx.heading("No stocks to compare", size="6"),
            rx.text(
                "Add stocks from the search bar or import from your cart",
                size="3",
                color=rx.color("gray", 10),
            ),
            rx.hstack(
                rx.button(
                    rx.icon("import", size=16),
                    "Import from Cart",
                    on_click=StockComparisonState.import_and_fetch_compare,
                    size="3",
                    variant="soft",
                ),
                spacing="3",
            ),
            spacing="4",
            align="center",
        ),
        height="60vh",
    )


def comparison_section() -> rx.Component:
    """Main comparison section."""
    return rx.cond(
        StockComparisonState.is_loading_data,
        loading_skeleton(),
        rx.cond(
            StockComparisonState.compare_list.length() > 0,
            rx.box(
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
            ),
            empty_state(),
        ),
    )


@rx.page(route="/analyze/compare", on_load=StockComparisonState.auto_load_from_cart)
def index() -> rx.Component:
    """Main page component."""
    return rx.fragment(
        loading_screen(),
        navbar(),
        rx.box(
            rx.link(
                rx.hstack(
                    rx.icon("chevron_left", size=22),
                    rx.text("analyze", margin_top="-2px"),
                    spacing="0",
                ),
                href="/analyze",
                underline="none",
            ),
            position="fixed",
            justify="center",
            style={"paddingTop": "1em", "paddingLeft": "0.5em"},
            z_index="1",
        ),
        rx.box(
            comparison_section(),
            width="100%",
            style={
                "max_width": "90vw",
                "margin": "0 auto",
            },
        ),
        drawer_button(),
        spacing="0",
    )
