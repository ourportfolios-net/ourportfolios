"""Performance and metrics cards for the ticker landing page."""

import reflex as rx

from ...components.cards import glass_card
from ...state.framework_state import GlobalFrameworkState
from .state import State


def performance_card_skeleton():
    """Skeleton for a single performance chart card"""
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.skeleton(height="1.5rem", width="8rem", border_radius="14px"),
                rx.spacer(),
                rx.skeleton(height="2rem", width="10rem", border_radius="14px"),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.skeleton(height="250px", width="100%", border_radius="14px"),
            spacing="2",
            align="stretch",
            height="100%",
        ),
        width="100%",
        height="100%",
        padding="0.75em",
    )


def create_dynamic_chart(category: str):
    """Create a dynamic chart for a specific category"""
    has_no_chart_data = State.get_chart_data_for_category[category].length() == 0

    return rx.cond(
        has_no_chart_data,
        performance_card_skeleton(),
        glass_card(
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
                            style={"border_radius": "14px"},
                        ),
                        rx.text("No metrics", size="1", color="gray"),
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
                        rx.recharts.y_axis(
                            tick={"fontSize": 14},
                        ),
                        rx.recharts.tooltip(),
                        data=State.get_chart_data_for_category[category],
                        width="100%",
                        height=250,
                        margin={"top": 15, "right": 30, "left": 10, "bottom": 5},
                    ),
                    width="100%",
                    height="250px",
                    style={"overflow": "hidden"},
                ),
                spacing="2",
                align="stretch",
                height="100%",
            ),
            width="100%",
            height="100%",
            padding="0.75em",
        ),
    )


def framework_indicator():
    """Show which framework is currently selected."""
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        rx.link(
            rx.hstack(
                rx.icon("target", size=16),
                rx.text(
                    f"Framework: {GlobalFrameworkState.framework_display_name}",
                    size="2",
                    weight="medium",
                ),
                rx.icon("external-link", size=14),
                spacing="2",
                align="center",
                padding="0.5em",
                style={
                    "backgroundColor": rx.color("violet", 2),
                    "border": f"1px solid {rx.color('violet', 4)}",
                    "borderRadius": "6px",
                    "transition": "all 0.2s ease",
                    "_hover": {
                        "backgroundColor": rx.color("violet", 3),
                        "borderColor": rx.color("violet", 5),
                        "transform": "translateY(-1px)",
                    },
                },
            ),
            href="/recommend",
            underline="none",
        ),
        None,
    )


def performance_cards():
    """Create performance cards with dynamic charts that adapt to any number of categories"""
    categories = State.get_categories_list

    # Use loading flag instead of checking data directly
    return rx.cond(
        State.is_loading_financial,
        # Show skeleton grid while loading
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
            grid_template_columns="repeat(3, 1fr)",
            gap="1rem",
            width="100%",
            style={"min_width": "0"},
        ),
        # Show actual content when loaded
        rx.vstack(
            rx.cond(
                ~GlobalFrameworkState.has_selected_framework,
                rx.callout.root(
                    rx.callout.icon(
                        rx.icon("target", size=20),
                    ),
                    rx.callout.text(
                        rx.hstack(
                            rx.text(
                                "No investment framework selected. ",
                                size="2",
                                weight="medium",
                            ),
                            rx.link(
                                rx.button(
                                    rx.icon("arrow-right", size=16),
                                    "Select a Framework",
                                    size="2",
                                    variant="soft",
                                    color_scheme="violet",
                                ),
                                href="/recommend",
                                underline="none",
                            ),
                            spacing="3",
                            align="center",
                        )
                    ),
                    color_scheme="violet",
                    variant="surface",
                    size="1",
                    style={"marginBottom": "1em"},
                ),
                None,
            ),
            rx.box(
                rx.foreach(
                    categories,
                    lambda category: create_dynamic_chart(category),
                ),
                display="grid",
                grid_template_columns="repeat(3, 1fr)",
                gap="1rem",
                width="100%",
                max_height="70vh",
                overflow="visible",
                style={"min_width": "0"},
            ),
            spacing="3",
            width="100%",
        ),
    )
