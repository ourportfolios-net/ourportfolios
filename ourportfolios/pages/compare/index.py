"""Simplified stock comparison page - compare multiple stocks side by side."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.loading import loading_screen
from ...state import StockComparisonState

from ourportfolios.pages.compare.comparison_table import comparison_section


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
