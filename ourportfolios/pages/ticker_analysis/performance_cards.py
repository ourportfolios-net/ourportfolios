"""Performance and metrics cards for the ticker landing page."""

import reflex as rx

from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.primitives import (
    heading,
    muted_text,
    skeleton_box,
    spacer,
    subheading,
    surface_box,
    vstack,
)
from ourportfolios.ui.theme import white
from ourportfolios.ui.theme.surfaces import RADIUS_BUTTON, RADIUS_INPUT

# ── Static placeholder data for guest view ────────────────────────────────────
_PLACEHOLDER_SERIES = [
    {"year": "2019", "value": 42},
    {"year": "2020", "value": 28},
    {"year": "2021", "value": 61},
    {"year": "2022", "value": 38},
    {"year": "2023", "value": 74},
    {"year": "2024", "value": 55},
    {"year": "2025", "value": 83},
]

_GUEST_CATEGORIES = [
    "Per Share Value",
    "Growth Rate",
    "Profitability",
    "Valuation",
    "Leverage & Liquidity",
    "Efficiency",
]

_GUEST_OVERLAY_STYLE = {
    "backdropFilter": "blur(10px)",
    "WebkitBackdropFilter": "blur(10px)",
    "backgroundColor": "rgba(8, 8, 14, 0.5)",
    "borderRadius": "0.625rem",
    "zIndex": "10",
}


def _skel(w: str, h: str) -> rx.Component:
    return skeleton_box(width=w, height=h)


def performance_card_skeleton():
    return surface_box(
        vstack(
            skeleton_box(width="40%", height="1.125rem"),
            spacer(),
            skeleton_box(width="30%", height="1.625rem"),
            spacing="3",
            align="stretch",
            height="100%",
        ),
        padding="0.75rem",
        width="100%",
        height="100%",
    )


def _placeholder_chart(label: str) -> rx.Component:
    """Blurred static chart card shown to guests."""
    return surface_box(
        vstack(
            subheading(label),
            spacer(),
            rx.box(
                width="7rem",
                height="1.625rem",
                background=white(0.07),
                border_radius=RADIUS_BUTTON,
            ),
            align="center",
            width="100%",
        ),
        rx.box(
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="value",
                    stroke=rx.color("accent", 9),
                    stroke_width=3,
                    type_="monotone",
                    dot=False,
                ),
                rx.recharts.x_axis(
                    data_key="year",
                    angle=-45,
                    text_anchor="end",
                    height=60,
                    tick={"fontSize": 14},
                ),
                rx.recharts.y_axis(tick={"fontSize": 14}),
                data=_PLACEHOLDER_SERIES,
                width="100%",
                height=250,
                margin={"top": 15, "right": 30, "left": 10, "bottom": 5},
            ),
            width="100%",
            height="15.625rem",
            overflow="hidden",
        ),
        spacing="2",
        align="stretch",
        height="100%",
        padding="0.75rem",
        width="100%",
    )


def guest_overlay() -> rx.Component:
    """Frosted overlay that sits above the blurred placeholder grid."""
    return rx.box(
        vstack(
            rx.icon("lock", size=24, color=white(0.35)),
            heading("Log in to get the full experience", level=3),
            muted_text(
                "Performance metrics and charts are available to registered users.",
                text_align="center",
                max_width="22rem",
            ),
            rx.box(
                rx.text(
                    "Sign in",
                    font_size="0.8125rem",
                    font_weight="500",
                    color=white(0.55),
                ),
                padding="0.35rem 0.85rem",
                border_radius=RADIUS_BUTTON,
                background=white(0.04),
                border=f"1px solid {white(0.09)}",
                cursor="pointer",
                transition="background 0.15s, border-color 0.15s",
                _hover={"background": white(0.08), "border_color": white(0.17)},
                on_click=AuthState.redirect_to_login_from_current_page,
            ),
            spacing="3",
            align="center",
            justify="center",
        ),
        position="absolute",
        top="0",
        left="0",
        right="0",
        bottom="0",
        display="flex",
        align_items="center",
        justify_content="center",
        style=_GUEST_OVERLAY_STYLE,
    )


def _guest_performance_grid() -> rx.Component:
    """6 blurred placeholder charts + the lock overlay."""
    return rx.box(
        # Placeholder grid (blurred via the overlay above)
        rx.box(
            *[_placeholder_chart(label) for label in _GUEST_CATEGORIES],
            display="grid",
            grid_template_columns="repeat(auto-fill, minmax(min(18rem, 100%), 1fr))",
            gap="1rem",
            width="100%",
            style={
                "min_width": "0",
                "filter": "blur(3px)",
                "pointerEvents": "none",
                "userSelect": "none",
            },
        ),
        guest_overlay(),
        position="relative",
        width="100%",
        height="100%",
        min_height="25rem",
        overflow="hidden",
        border_radius=RADIUS_INPUT,
    )


def create_dynamic_chart(category: str):
    has_no_chart_data = State.get_chart_data_for_category[category] == []

    return rx.cond(
        has_no_chart_data,
        performance_card_skeleton(),
        surface_box(
            vstack(
                subheading(category),
                spacer(),
                rx.cond(
                    State.available_metrics_by_category.get(category, []) != [],
                    rx.select(
                        State.available_metrics_by_category[category],
                        value=State.selected_metrics.get(category, ""),
                        on_change=lambda value: State.set_metric_for_category(
                            category,
                            value,
                        ),
                        size="1",
                        style={
                            "border_radius": RADIUS_BUTTON,
                            "background": white(0.04),
                            "border": f"1px solid {white(0.09)}",
                            "color": "white",
                        },
                    ),
                    muted_text("No metrics", size="1"),
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.box(
                rx.recharts.line_chart(
                    rx.recharts.line(
                        data_key="value",
                        stroke=rx.color("accent", 9),
                        stroke_width=3,
                        type_="monotone",
                        dot=False,
                    ),
                    rx.recharts.x_axis(
                        data_key="year",
                        angle=-45,
                        text_anchor="end",
                        height=60,
                        tick={"fontSize": 14},
                    ),
                    rx.recharts.y_axis(tick={"fontSize": 14}),
                    rx.recharts.tooltip(),
                    data=State.get_chart_data_for_category[category],
                    width="100%",
                    height=250,
                    margin={"top": 15, "right": 30, "left": 10, "bottom": 5},
                ),
                width="100%",
                height="15.625rem",
                overflow="hidden",
            ),
            spacing="2",
            align="stretch",
            height="100%",
            padding="0.75rem",
            width="100%",
        ),
    )


def _performance_cards_content() -> rx.Component:
    categories = State.get_categories_list

    return rx.cond(
        ~AuthState.is_authenticated,
        # ── Guest & Loading: placeholder grid + lock overlay ──────────
        _guest_performance_grid(),
        # ── Authenticated: real charts ────────────────────────────────────────
        rx.cond(
            State.is_loading_financial,
            rx.box(
                rx.fragment(
                    performance_card_skeleton(),
                    performance_card_skeleton(),
                    performance_card_skeleton(),
                    performance_card_skeleton(),
                    performance_card_skeleton(),
                    performance_card_skeleton(),
                ),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(min(18rem, 100%), 1fr))",
                gap="1rem",
                width="100%",
                style={"min_width": "0"},
            ),
            rx.box(
                rx.foreach(
                    categories,
                    create_dynamic_chart,
                ),
                display="grid",
                grid_template_columns="repeat(auto-fill, minmax(min(18rem, 100%), 1fr))",
                gap="1rem",
                width="100%",
                style={"min_width": "0"},
            ),
        ),
    )


def performance_cards():
    return rx.fragment(
        rx.box(
            rx.cond(
                AuthState.is_authenticated,
                rx.scroll_area(
                    _performance_cards_content(),
                    scrollbars="vertical",
                    type="hover",
                    height="100%",
                ),
                rx.box(
                    _performance_cards_content(),
                    height="100%",
                    width="100%",
                    overflow="hidden",
                ),
            ),
            display=["block", "block", "none"],
            height="calc(100vh - 17rem)",
            width="100%",
        ),
        rx.box(
            _performance_cards_content(),
            display=["none", "none", "block"],
            width="100%",
            height="100%",
            overflow="hidden",
        ),
    )
