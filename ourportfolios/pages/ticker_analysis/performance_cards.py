"""Performance and metrics cards for the ticker landing page."""

import reflex as rx

from ...styles import white, CARD_BORDER
from .state import State

_CARD_RADIUS = "0.625rem"


def _skel(w: str, h: str) -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        style={"border_radius": "0.375rem"},
    )


def performance_card_skeleton():
    return rx.box(
        rx.vstack(
            rx.hstack(
                _skel("40%", "1.125rem"),
                rx.spacer(),
                _skel("30%", "1.625rem"),
                align="center",
                width="100%",
            ),
            _skel("100%", "15.625rem"),
            spacing="3",
            align="stretch",
            height="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="0.75rem",
        width="100%",
        height="100%",
    )


def create_dynamic_chart(category: str):
    has_no_chart_data = State.get_chart_data_for_category[category].length() == 0

    return rx.cond(
        has_no_chart_data,
        performance_card_skeleton(),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading(category, size="4", weight="medium"),
                    rx.spacer(),
                    rx.cond(
                        State.available_metrics_by_category.contains(category),
                        rx.select(
                            State.available_metrics_by_category[category],
                            value=State.selected_metrics.get(category, ""),
                            on_change=lambda value: State.set_metric_for_category(
                                category, value
                            ),
                            size="1",
                            style={
                                "border_radius": "0.5rem",
                                "background": white(0.04),
                                "border": f"1px solid {white(0.09)}",
                                "color": "white",
                            },
                        ),
                        rx.text("No metrics", size="1", color=white(0.3)),
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
                    style={"overflow": "hidden"},
                ),
                spacing="2",
                align="stretch",
                height="100%",
            ),
            background=white(0.025),
            border=CARD_BORDER,
            border_radius=_CARD_RADIUS,
            padding="0.75rem",
            width="100%",
            height="100%",
        ),
    )


def performance_cards():
    categories = State.get_categories_list

    return rx.cond(
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
                lambda category: create_dynamic_chart(category),
            ),
            display="grid",
            grid_template_columns="repeat(auto-fill, minmax(min(18rem, 100%), 1fr))",
            gap="1rem",
            width="100%",
            max_height="70vh",
            overflow="visible",
            style={"min_width": "0"},
        ),
    )
