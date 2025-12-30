"""Company information components - FIXED."""

import reflex as rx
from .state import State


def company_info_card_skeleton():
    return rx.card(
        rx.vstack(
            rx.box(
                rx.skeleton(height="2.5rem", width="12rem", border_radius="8px"),
                width="100%",
                display="flex",
                justify_content="center",
            ),
            rx.box(
                rx.skeleton(height="220px", width="220px", border_radius="50%"),
                width="100%",
                display="flex",
                justify_content="center",
                align_items="center",
                style={"marginTop": "2.5em", "marginBottom": "2.5em"},
            ),
            rx.card(
                rx.vstack(
                    *[
                        rx.box(
                            rx.hstack(
                                rx.skeleton(height="1.2rem", width="8rem"),
                                rx.skeleton(
                                    height="1.2rem", width="3rem", border_radius="12px"
                                ),
                                align="center",
                                justify="between",
                                width="100%",
                            ),
                            rx.skeleton(height="1rem", width="10rem"),
                            width="100%",
                        )
                        for _ in range(3)
                    ],
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),
            justify="center",
            align="center",
            width="100%",
            spacing="0",
        ),
        width="100%",
        flex=0.6,
        min_width=0,
        max_width="20em",
    )


def shareholders_pie_chart():
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


def company_generic_info_card():
    # Use loading flag instead of checking data
    return rx.cond(
        State.is_loading_company,
        company_info_card_skeleton(),
        rx.card(
            rx.vstack(
                rx.box(
                    rx.segmented_control.root(
                        rx.segmented_control.item("Shares", value="shares"),
                        rx.segmented_control.item("Events", value="events"),
                        rx.segmented_control.item("News", value="news"),
                        on_change=State.set_company_control,
                        value=State.company_control,
                        size="3",
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
                            style={"marginTop": "2.5em", "marginBottom": "2.5em"},
                        ),
                        rx.card(
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
                                                rx.badge(
                                                    f"{officer['officer_own_percent']}%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                    high_contrast=True,
                                                ),
                                                align="center",
                                            ),
                                            rx.text(
                                                officer["officer_position"], size="2"
                                            ),
                                        ),
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                style={"height": "24.3em"},
                            ),
                            width="100%",
                        ),
                        justify="center",
                        align="center",
                        width="100%",
                    ),
                    rx.cond(
                        State.company_control == "events",
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.events,
                                    lambda event: rx.card(
                                        rx.hstack(
                                            rx.heading(
                                                event["event_name"],
                                                weight="medium",
                                                size="3",
                                            ),
                                            rx.badge(f"{event['price_change_ratio']}%"),
                                            align="center",
                                        ),
                                        rx.text(
                                            event["event_desc"],
                                            weight="regular",
                                            size="1",
                                        ),
                                    ),
                                ),
                                spacing="3",
                            ),
                            style={"height": "45.3em"},
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.news,
                                    lambda news: rx.card(
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
                                                rx.badge(
                                                    f"{news['price_change_ratio']}%"
                                                ),
                                            ),
                                            align="center",
                                            justify="between",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                            ),
                            spacing="2",
                            width="100%",
                            style={"height": "45.3em"},
                        ),
                    ),
                ),
                justify="center",
                align="center",
                width="100%",
                style={"height": "100%"},
            ),
            width="100%",
            flex=0.6,
            min_width=0,
            max_width="20em",
            style={"height": "100%"},
        ),
    )
