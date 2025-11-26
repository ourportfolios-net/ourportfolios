"""Stock comparison page - compare multiple stocks side by side."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.loading import loading_screen
from ...state import StockComparisonState

from .controls import comparison_controls
from .comparison_cards import stock_metric_cell


def comparison_table_section() -> rx.Component:
    """Table view of comparison data (rotated 90 degrees - horizontal tickers, vertical metrics)"""
    return rx.hstack(
        # Fixed ticker symbols column on the left
        rx.box(
            rx.vstack(
                # Empty space for metric labels header
                rx.box(
                    height="3.5em",
                    width="15em",
                ),
                # Scrollable stocks area (vertical only)
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
                                                rx.text(
                                                    f"{stock.get('market_cap', '')} B. VND",
                                                    size="1",
                                                    color=rx.color("gray", 10),
                                                    weight="medium",
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
                                    _hover={
                                        "marginLeft": "0",
                                    },
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
        # Single scroll area for all metrics (horizontal + vertical)
        rx.scroll_area(
            rx.vstack(
                # Metric labels at the top
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
                                width="10em",
                                min_width="10em",
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
                # All industries and stocks
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
    """Main comparison section with industry-grouped layout"""
    return rx.cond(
        StockComparisonState.compare_list,
        rx.box(
            rx.vstack(
                comparison_controls(),
                # Table view with inline graphs
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
        rx.center(
            rx.vstack(
                rx.text(
                    "Your compare list is empty. ",
                    size="3",
                    weight="medium",
                    align="center",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("shopping_cart", size=16),
                        rx.text("Import from Cart"),
                        spacing="2",
                    ),
                    on_click=StockComparisonState.import_and_fetch_compare,
                    size="3",
                ),
                spacing="3",
                align="center",
            ),
            min_height="40vh",
            width="100%",
        ),
    )


@rx.page(route="/analyze/compare")
def index() -> rx.Component:
    """Main page component"""
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
