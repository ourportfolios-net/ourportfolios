"""Framework recommendation page - select investment frameworks."""

import reflex as rx

from ...components.navbar import navbar
from ...components.breadcrumb import breadcrumb

from .state import FrameworkState
from .framework_cards import category_filter_button, framework_card, skeleton_card
from .framework_dialog import framework_dialog
from .add_framework_dialog import add_framework_dialog, add_metric_selector


def page_header():
    """Page header"""
    return rx.vstack(
        breadcrumb("/framework", tail_label="Frameworks"),
        rx.heading(
            "Choose Your Framework",
            size="8",
            weight="bold",
            color="white",
        ),
        rx.text(
            "Select a pre-built investment strategy model to decode market noise and identify high-potential assets.",
            size="3",
            color="rgba(255,255,255,0.4)",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def toolbar():
    """Filters + search + add all on one row"""
    return rx.hstack(
        # Category filters — left side
        rx.hstack(
            rx.foreach(FrameworkState.categories, category_filter_button),
            spacing="2",
            wrap="nowrap",
            flex_shrink="0",
        ),
        rx.spacer(),
        # Search + Add — right side
        rx.hstack(
            rx.box(
                rx.icon(
                    "search",
                    size=14,
                    color="rgba(255,255,255,0.25)",
                    style={
                        "position": "absolute",
                        "left": "10px",
                        "top": "50%",
                        "transform": "translateY(-50%)",
                        "pointer_events": "none",
                    },
                ),
                rx.input(
                    placeholder="Search frameworks...",
                    value=FrameworkState.search_query,
                    on_change=FrameworkState.set_search_query,
                    size="2",
                    style={
                        "background": "rgba(255,255,255,0.04)",
                        "border": "1px solid rgba(255,255,255,0.08)",
                        "border_radius": "8px",
                        "color": "white",
                        "padding_left": "2rem",
                        "width": "280px",
                        "_placeholder": {"color": "rgba(255,255,255,0.22)"},
                        "_focus": {
                            "border_color": "rgba(139,92,246,0.4)",
                            "outline": "none",
                        },
                    },
                ),
                position="relative",
                display="flex",
                align_items="center",
            ),
            rx.button(
                rx.icon("plus", size=14),
                "Add Framework",
                on_click=FrameworkState.open_add_dialog,
                size="2",
                style={
                    "background": "rgba(255,255,255,0.05)",
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "border_radius": "8px",
                    "color": "rgba(255,255,255,0.7)",
                    "font_weight": "500",
                    "cursor": "pointer",
                    "transition": "all 0.15s ease",
                    "_hover": {
                        "background": "rgba(255,255,255,0.09)",
                        "border_color": "rgba(255,255,255,0.18)",
                        "color": "white",
                    },
                },
            ),
            spacing="2",
            align="center",
            flex_shrink="0",
        ),
        width="100%",
        align="center",
    )


def skeleton_grid() -> rx.Component:
    """Grid of skeleton cards shown while loading."""
    return rx.box(
        *[skeleton_card() for _ in range(6)],
        display="grid",
        grid_template_columns="repeat(auto-fill, minmax(360px, 1fr))",
        gap="1rem",
        width="100%",
    )


def frameworks_grid():
    """Grid of framework cards"""
    return rx.cond(
        FrameworkState.loading_frameworks,
        skeleton_grid(),
        rx.cond(
            FrameworkState.frameworks.length() > 0,
            rx.box(
                rx.foreach(FrameworkState.frameworks, framework_card),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(360px, 1fr))",
                gap="1rem",
                width="100%",
            ),
            skeleton_grid(),
        ),
    )


def main_content():
    """Main content area"""
    return rx.vstack(
        page_header(),
        rx.box(height="1px", width="100%", background="rgba(255,255,255,0.06)"),
        toolbar(),
        frameworks_grid(),
        spacing="5",
        width="100%",
    )


@rx.page(route="/framework", on_load=[FrameworkState.on_mount])
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
            padding_top="3em",
            padding_bottom="5em",
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
