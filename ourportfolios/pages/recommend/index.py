"""Framework recommendation page - select investment frameworks."""

import reflex as rx

from ...components.navbar import navbar

from .state import FrameworkState
from .framework_cards import category_filter_button, framework_card
from .framework_dialog import framework_dialog
from .add_framework_dialog import add_framework_dialog, add_metric_selector


def page_header():
    """Page header"""
    return rx.vstack(
        rx.heading("Choose Your Framework", size="8"),
        rx.text(
            "Select a pre-built investment strategy model to decode market noise and identify high-potential assets.",
            size="3",
            color="gray",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def category_filters():
    """Category filter buttons"""
    return rx.hstack(
        rx.foreach(FrameworkState.categories, category_filter_button),
        spacing="3",
        width="100%",
        wrap="wrap",
    )


def frameworks_grid():
    """Grid of framework cards"""
    return rx.cond(
        FrameworkState.loading_frameworks,
        rx.center(rx.spinner(size="3"), height="400px"),
        rx.cond(
            FrameworkState.frameworks.length() > 0,
            rx.box(
                rx.foreach(FrameworkState.frameworks, framework_card),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(320px, 1fr))",
                gap="1.5rem",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("search", size=48, color="gray"),
                    rx.text("No frameworks found", size="4", color="gray"),
                    spacing="3",
                ),
                height="400px",
            ),
        ),
    )


def main_content():
    """Main content area"""
    return rx.vstack(
        page_header(),
        category_filters(),
        rx.hstack(
            rx.input(
                placeholder="Search strategies...",
                value=FrameworkState.search_query,
                on_change=FrameworkState.set_search_query,
                size="3",
            ),
            rx.button(
                rx.icon("plus", size=18),
                "Add Framework",
                on_click=FrameworkState.open_add_dialog,
                size="3",
                variant="soft",
            ),
            spacing="3",
            width="100%",
        ),
        frameworks_grid(),
        spacing="5",
        width="100%",
    )


@rx.page(route="/recommend", on_load=[FrameworkState.on_mount])
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                main_content(),
                width="90vw",
                max_width="1800px",
            ),
            width="100%",
            padding="2em",
            padding_top="6em",
        ),
        framework_dialog(),
        add_framework_dialog(),
        add_metric_selector(),
        on_unmount=FrameworkState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
    )
