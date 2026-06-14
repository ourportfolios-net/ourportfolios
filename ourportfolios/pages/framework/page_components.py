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
from ourportfolios.ui.primitives import (
    heading,
    muted_text,
    search_icon,
    search_input,
)
from ourportfolios.ui.theme.surfaces import BUTTON_SECONDARY
from ourportfolios.ui.tokens import RADIUS_SM


def _page_header() -> rx.Component:
    return rx.vstack(
        breadcrumb("/framework", tail_label="Frameworks"),
        heading("Choose Your Framework", level=1),
        muted_text(
            "Select a pre-built investment strategy model to decode market noise and identify high-potential assets.",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def _search_box() -> rx.Component:
    return rx.box(
        search_icon(),
        search_input(
            placeholder="Search frameworks...",
            value=FrameworkState.search_query,
            on_change=FrameworkState.set_search_query,
            size="2",
        ),
        position="relative",
        display="flex",
        align_items="center",
        flex="1",
        max_width=["100%", "100%", "17.5rem"],
        min_width="0",
    )


def _add_framework_button() -> rx.Component:
    return rx.button(
        rx.icon("plus", size=14),
        "Add Framework",
        on_click=FrameworkState.open_add_dialog,
        size="2",
        style={**BUTTON_SECONDARY, "border_radius": RADIUS_SM},
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
            _add_framework_button(),
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
            rx.icon("inbox", size=36, color="rgba(255,255,255,0.2)"),
            rx.text("No frameworks found", size="4", weight="medium", color="rgba(255,255,255,0.4)"),
            muted_text("Try adjusting your search or filter."),
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
