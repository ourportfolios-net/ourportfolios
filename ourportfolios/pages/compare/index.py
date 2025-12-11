"""Stock comparison page - compare multiple stocks side by side."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.loading import loading_screen
from ...state import StockComparisonState

from .controls import comparison_controls
from .comparison_cards import metric_labels_column, industry_group_section


def comparison_section() -> rx.Component:
    """Main comparison section with industry-grouped layout"""
    return rx.cond(
        StockComparisonState.compare_list,
        rx.box(
            rx.vstack(
                comparison_controls(),
                # Main comparison table
                rx.hstack(
                    # Fixed metric labels column
                    metric_labels_column(),
                    # Scrollable grouped stock columns area
                    rx.box(
                        rx.scroll_area(
                            rx.box(
                                rx.hstack(
                                    # Industry groups
                                    rx.foreach(
                                        StockComparisonState.grouped_stocks.items(),
                                        lambda item: industry_group_section(
                                            item[0],
                                            item[1],
                                        ),
                                    ),
                                    spacing="7",  # Space between industry groups
                                    align="start",
                                    style={"flex_wrap": "nowrap"},
                                ),
                                padding_top="0.5em",
                                padding_bottom="0.5em",
                            ),
                            direction="horizontal",
                            scrollbars="horizontal",
                            style={
                                "width": "100%",
                                "maxWidth": "90vw",
                                "overflowX": "auto",
                                "overflowY": "hidden",
                            },
                        ),
                        width="100%",
                        margin_left="1.8em",
                        style={
                            "maxWidth": "90vw",
                            "overflowX": "auto",
                            "overflowY": "hidden",
                            "position": "relative",
                        },
                    ),
                    spacing="0",
                    align="start",
                    width="100%",
                    style={"flex_wrap": "nowrap"},
                ),
                spacing="0",
                width="100%",
            ),
            width="100%",
            style={
                "max_width": "100vw",
                "margin": "0 auto",
                "padding": "1.5em",
                "overflowX": "hidden",
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
