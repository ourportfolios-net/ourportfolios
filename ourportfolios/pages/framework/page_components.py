"""Framework page UI components."""

import reflex as rx

from ourportfolios.components.breadcrumb import breadcrumb
from ourportfolios.components.navbar import navbar
from ourportfolios.pages.framework.add_framework_dialog import (
    add_framework_dialog,
    add_metric_selector,
)
from ourportfolios.pages.framework.framework_cards import (
    category_filter_button,
    framework_card,
    skeleton_card,
)
from ourportfolios.pages.framework.framework_dialog import framework_dialog
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.styles import white


def _page_header() -> rx.Component:
    return rx.vstack(
        breadcrumb("/framework", tail_label="Frameworks"),
        rx.heading("Choose Your Framework", size="8", weight="bold", color="white"),
        rx.text(
            "Select a pre-built investment strategy model to decode market noise and identify high-potential assets.",
            size="3",
            color="rgba(255,255,255,0.4)",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def _search_box() -> rx.Component:
    return rx.box(
        rx.icon(
            "search",
            size=14,
            color="rgba(255,255,255,0.25)",
            position="absolute",
            left="0.625rem",
            top="50%",
            transform="translateY(-50%)",
            pointer_events="none",
        ),
        rx.input(
            placeholder="Search frameworks...",
            value=FrameworkState.search_query,
            on_change=FrameworkState.set_search_query,
            size="2",
            background="rgba(255,255,255,0.04)",
            border="1px solid rgba(255,255,255,0.08)",
            border_radius="0.5rem",
            color="white",
            padding_left="2rem",
            width="100%",
            _placeholder={"color": "rgba(255,255,255,0.22)"},
            _focus={"border_color": "rgba(139,92,246,0.4)", "outline": "none"},
        ),
        position="relative",
        display="flex",
        align_items="center",
        flex="1",
        max_width=["100%", "100%", "17.5rem"],
        min_width="0",
    )


def _add_framework_btn() -> rx.Component:
    return rx.button(
        rx.icon("plus", size=14),
        "Add Framework",
        on_click=FrameworkState.open_add_dialog,
        size="2",
        background="rgba(255,255,255,0.05)",
        border="1px solid rgba(255,255,255,0.1)",
        border_radius="0.5rem",
        color="rgba(255,255,255,0.7)",
        font_weight="500",
        white_space="nowrap",
        flex_shrink="0",
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={
            "background": "rgba(255,255,255,0.09)",
            "border_color": "rgba(255,255,255,0.18)",
            "color": "white",
        },
    )


def _toolbar() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.foreach(FrameworkState.categories, category_filter_button),
            wrap="wrap",
            gap="0.5rem",
            align="center",
            flex="1",
            min_width="0",
        ),
        rx.hstack(
            _search_box(),
            _add_framework_btn(),
            spacing="2",
            align="center",
            flex_shrink="0",
            width=["100%", "100%", "auto"],
        ),
        width="100%",
        align="center",
        wrap="wrap",
        gap="0.75rem",
    )


def _skeleton_grid() -> rx.Component:
    return rx.box(
        *[skeleton_card() for _ in range(6)],
        display="grid",
        grid_template_columns="repeat(auto-fill, minmax(min(22.5rem, 100%), 1fr))",
        gap="1rem",
        width="100%",
    )


def _empty_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("inbox", size=36, color=white(0.2)),
            rx.text("No frameworks found", size="4", weight="medium", color=white(0.4)),
            rx.text(
                "Try adjusting your search or filter.", size="2", color=white(0.25),
            ),
            spacing="2",
            align="center",
        ),
        width="100%",
        padding_y="5rem",
    )


def _frameworks_grid() -> rx.Component:
    return rx.cond(
        FrameworkState.loading_frameworks,
        _skeleton_grid(),
        rx.cond(
            FrameworkState.frameworks.length() > 0,
            rx.box(
                rx.foreach(FrameworkState.frameworks, framework_card),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(min(22.5rem, 100%), 1fr))",
                gap="1rem",
                width="100%",
            ),
            _empty_state(),
        ),
    )


def page_body() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.vstack(
                    _page_header(),
                    rx.box(
                        height="1px", width="100%", background="rgba(255,255,255,0.06)",
                    ),
                    _toolbar(),
                    _frameworks_grid(),
                    spacing="5",
                    width="100%",
                ),
                width="86vw",
                max_width="90rem",
                margin="0 auto",
            ),
            width="100%",
            padding_x=["1rem", "1.5rem", "2rem"],
            padding_top=["1.5rem", "2rem", "3em"],
            padding_bottom=["3rem", "4rem", "5em"],
        ),
        framework_dialog(),
        add_framework_dialog(),
        add_metric_selector(),
    )
