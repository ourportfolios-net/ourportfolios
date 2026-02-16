"""Framework recommendation page - select investment frameworks."""

import reflex as rx

from ...components.navbar import navbar
from ...components.page_roller import card_roller, card_link

from .state import FrameworkState
from .framework_cards import category_filter_button, framework_card, ticker_cart_sidebar
from .framework_dialog import framework_dialog
from .add_framework_dialog import add_framework_dialog, add_metric_selector


def page_header():
    """Command center style header with step indicator"""
    return rx.vstack(
        # Step indicator
        rx.hstack(
            rx.icon("link", size=16, color="#8B5CF6"),
            rx.text(
                "STEP 01",
                size="2",
                weight="bold",
                color="#8B5CF6",
                style={"letter_spacing": "0.1em"},
            ),
            spacing="2",
            align="center",
        ),
        # Main heading
        rx.heading(
            "Choose Your Framework",
            size="9",
            weight="bold",
            style={
                "background": "linear-gradient(135deg, #FFFFFF 0%, #A78BFA 100%)",
                "background_clip": "text",
                "color": "transparent",
            },
        ),
        # Description
        rx.text(
            "Select a pre-built investment strategy model to decode market noise and identify high-potential assets.",
            size="4",
            color="gray",
            style={"max_width": "800px", "line_height": "1.6"},
        ),
        spacing="3",
        align="start",
        width="100%",
        padding_bottom="2em",
    )


def category_filters():
    """Horizontal category filter buttons"""
    return rx.hstack(
        rx.foreach(FrameworkState.categories, category_filter_button),
        spacing="3",
        width="100%",
        wrap="wrap",
        padding_y="1.5em",
    )


def frameworks_grid():
    """Grid layout for framework cards"""
    return rx.cond(
        FrameworkState.loading_frameworks,
        rx.center(rx.spinner(size="3", color="#8B5CF6"), height="400px"),
        rx.cond(
            FrameworkState.frameworks.length() > 0,
            rx.box(
                rx.foreach(FrameworkState.frameworks, framework_card),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(320px, 1fr))",
                gap="1.5em",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("search", size=48, color="gray"),
                    rx.text(
                        "No frameworks found in this category", size="4", color="gray"
                    ),
                    spacing="3",
                    align="center",
                ),
                height="400px",
            ),
        ),
    )


def main_content_area():
    """Main content area with frameworks and cart"""
    return rx.hstack(
        # Left side - frameworks
        rx.vstack(
            page_header(),
            category_filters(),
            # Search and add button
            rx.hstack(
                rx.input(
                    placeholder="Search strategies...",
                    value=FrameworkState.search_query,
                    on_change=FrameworkState.set_search_query,
                    size="3",
                    style={
                        "background": "rgba(30, 30, 35, 0.6)",
                        "border": "1px solid rgba(139, 92, 246, 0.2)",
                        "border_radius": "0.75em",
                        "flex": "1",
                    },
                ),
                rx.button(
                    rx.icon("plus", size=18),
                    "Add Framework",
                    on_click=FrameworkState.open_add_dialog,
                    size="3",
                    variant="soft",
                    color_scheme="violet",
                ),
                spacing="3",
                width="100%",
            ),
            frameworks_grid(),
            spacing="0",
            width="100%",
            flex="1",
        ),
        # Right side - ticker cart
        ticker_cart_sidebar(),
        spacing="5",
        width="100%",
        align="start",
    )


@rx.page(route="/recommend", on_load=[FrameworkState.on_mount])
def index() -> rx.Component:
    return rx.box(
        rx.fragment(
            navbar(),
            # Main container
            rx.center(
                rx.box(
                    main_content_area(),
                    width="90vw",
                    max_width="1800px",
                ),
                width="100%",
                padding="2em",
                padding_top="6em",
            ),
            # Dialogs
            framework_dialog(),
            add_framework_dialog(),
            add_metric_selector(),
        ),
        on_unmount=FrameworkState.on_unmount,
        style={
            "background": "#090909",
            "color": "white",
            "min_height": "100vh",
            "width": "100%",
            "overflow_x": "hidden",
        },
    )
