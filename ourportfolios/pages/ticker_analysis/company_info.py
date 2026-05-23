"""Company information components."""

import reflex as rx

from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.ui.primitives import badge, skeleton_box
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import CARD_BORDER
from ourportfolios.ui.tokens import RADIUS_MD, RADIUS_SM

# Responsive heights: [mobile, desktop]
_SCROLL_HEIGHT_SHARES = ["28em", "24.3em"]
_SCROLL_HEIGHT_EVENTS = ["37em", "45.3em"]
_SCROLL_HEIGHT_NEWS = ["37em", "45.3em"]


def _officer_row_skeleton() -> rx.Component:
    """Skeleton for a single officer row (name + badge on left, position below)."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                skeleton_box(width="55%", height="1.25rem"),
                rx.spacer(),
                skeleton_box(width="4rem", height="1.25rem", radius="0.375rem"),
                width="100%",
                align="center",
            ),
            skeleton_box(width="35%", height="0.875rem"),
            spacing="1",
            width="100%",
        ),
        width="100%",
    )


def company_info_card_skeleton() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Segmented control skeleton
            rx.hstack(
                skeleton_box(width="3.75rem", height="1.75rem"),
                skeleton_box(width="3.75rem", height="1.75rem"),
                skeleton_box(width="3.125rem", height="1.75rem"),
                spacing="2",
                width="100%",
                justify="center",
            ),
            # Pie chart skeleton
            rx.box(
                rx.skeleton(
                    rx.box(width="10rem", height="10rem"),
                    loading=True,
                    style={"border_radius": "50%"},
                ),
                width="100%",
                display="flex",
                justify_content="center",
                align_items="center",
                style={"marginTop": "1.5em", "marginBottom": "1.5em"},
            ),
            # Officers list skeleton — matches the real subtle_box container
            rx.box(
                rx.vstack(
                    *[_officer_row_skeleton() for _ in range(6)],
                    spacing="3",
                    width="100%",
                ),
                background=white(0.02),
                border=f"1px solid {white(0.05)}",
                border_radius=RADIUS_SM,
                padding="0.75rem",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=RADIUS_MD,
        padding="1.25rem",
        width="100%",
        flex=["1", "1", "0.6"],
        min_width="0",
        max_width=["100%", "100%", "20em"],
    )


def shareholders_pie_chart() -> rx.Component:
    return rx.recharts.PieChart.create(
        rx.recharts.Pie.create(
            data=State.pie_data,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            outer_radius=90,
            label=False,
        ),
        rx.recharts.GraphingTooltip.create(view_box={"width": 100, "height": 50}),
        width=220,
        height=220,
    )


def company_generic_info_card() -> rx.Component:
    return rx.cond(
        State.is_loading_company,
        company_info_card_skeleton(),
        rx.box(
            rx.vstack(
                rx.box(
                    rx.segmented_control.root(
                        rx.segmented_control.item("Shares", value="shares"),
                        rx.segmented_control.item("Events", value="events"),
                        rx.segmented_control.item("News", value="news"),
                        on_change=State.set_company_control,
                        value=State.company_control,
                        size="2",
                        style={
                            "border_radius": RADIUS_SM,
                            "background": white(0.03),
                            "border": f"1px solid {white(0.07)}",
                            "padding": "0.2em",
                        },
                    ),
                    width="100%",
                    display="flex",
                    justify_content="center",
                ),
                rx.cond(
                    State.company_control == "shares",
                    rx.vstack(
                        rx.box(
                            shareholders_pie_chart(),
                            width="100%",
                            display="flex",
                            justify_content="center",
                            align_items="center",
                            style={"marginTop": "1.5em", "marginBottom": "1.5em"},
                            flex_shrink="0",
                        ),
                        rx.box(
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        State.officers,
                                        lambda officer: rx.box(
                                            rx.hstack(
                                                rx.heading(
                                                    officer["officer_name"],
                                                    weight="medium",
                                                    size="3",
                                                ),
                                                badge(
                                                    f"{officer['officer_own_percent']}%",
                                                    color_variant="gray",
                                                ),
                                                align="center",
                                                justify="between",
                                                width="100%",
                                            ),
                                            rx.text(
                                                officer["officer_position"],
                                                size="2",
                                                color=white(0.45),
                                            ),
                                            width="100%",
                                        ),
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                style={
                                    "height": _SCROLL_HEIGHT_SHARES,
                                    "minHeight": _SCROLL_HEIGHT_SHARES[0],
                                },
                            ),
                            background=white(0.02),
                            border=f"1px solid {white(0.05)}",
                            border_radius=RADIUS_SM,
                            padding="0.75rem",
                            width="100%",
                            flex="1",
                        ),
                        justify="start",
                        align="stretch",
                        width="100%",
                        flex="1",
                    ),
                    rx.cond(
                        State.company_control == "events",
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.events,
                                    lambda event: rx.box(
                                        rx.hstack(
                                            rx.heading(
                                                event["event_name"],
                                                weight="medium",
                                                size="3",
                                            ),
                                            rx.cond(
                                                event["price_change_ratio"].to(float) > 0,
                                                badge(f"{event['price_change_ratio']}%", color_variant="green"),
                                                rx.cond(
                                                    event["price_change_ratio"].to(float) < 0,
                                                    badge(f"{event['price_change_ratio']}%", color_variant="red"),
                                                    badge(f"{event['price_change_ratio']}%", color_variant="gray"),
                                                ),
                                            ),
                                            align="center",
                                        ),
                                        rx.text(
                                            event["event_desc"],
                                            weight="regular",
                                            size="1",
                                            color=white(0.45),
                                        ),
                                        background=white(0.02),
                                        border=f"1px solid {white(0.05)}",
                                        border_radius=RADIUS_SM,
                                        padding="0.75rem",
                                        width="100%",
                                    ),
                                ),
                                spacing="3",
                            ),
                            style={
                                "height": _SCROLL_HEIGHT_EVENTS,
                                "minHeight": _SCROLL_HEIGHT_SHARES[0],
                            },
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.news,
                                    lambda news: rx.box(
                                        rx.hstack(
                                            rx.text(
                                                f"{news['title']} ({news['publish_date']})",
                                                weight="regular",
                                                size="2",
                                            ),
                                            rx.cond(
                                                (news["price_change_ratio"] is not None)
                                                & ~(
                                                    news["price_change_ratio"]
                                                    != news["price_change_ratio"]
                                                ),
                                                rx.cond(
                                                    news["price_change_ratio"].to(float) > 0,
                                                    badge(f"{news['price_change_ratio']}%", color_variant="green"),
                                                    rx.cond(
                                                        news["price_change_ratio"].to(float) < 0,
                                                        badge(f"{news['price_change_ratio']}%", color_variant="red"),
                                                        badge(f"{news['price_change_ratio']}%", color_variant="gray"),
                                                    ),
                                                ),
                                            ),
                                            align="center",
                                            justify="between",
                                            width="100%",
                                        ),
                                        background=white(0.02),
                                        border=f"1px solid {white(0.05)}",
                                        border_radius=RADIUS_SM,
                                        padding="0.75rem",
                                        width="100%",
                                    ),
                                ),
                            ),
                            spacing="2",
                            width="100%",
                            style={
                                "height": _SCROLL_HEIGHT_NEWS,
                                "minHeight": _SCROLL_HEIGHT_SHARES[0],
                            },
                        ),
                    ),
                ),
                justify="center",
                align="center",
                width="100%",
                style={"height": "100%"},
            ),
            background=white(0.025),
            border=CARD_BORDER,
            border_radius=RADIUS_MD,
            padding="1.25rem",
            width="100%",
            flex=["1", "1", "0.6"],
            min_width="0",
            max_width=["100%", "100%", "20em"],
            style={"height": "100%"},
        ),
    )
