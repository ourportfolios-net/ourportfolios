"""Company information components."""

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


def company_info_card_skeleton():
    return rx.box(
        rx.vstack(
            # Segmented control placeholder
            rx.hstack(
                _skel("3.75rem", "1.75rem"),
                _skel("3.75rem", "1.75rem"),
                _skel("3.125rem", "1.75rem"),
                spacing="2",
                width="100%",
                justify="center",
            ),
            # Pie chart placeholder
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
            # List rows
            rx.box(
                rx.vstack(
                    *[
                        rx.hstack(
                            _skel("55%", "0.875rem"),
                            rx.spacer(),
                            _skel("25%", "0.875rem"),
                            width="100%",
                            align="center",
                        )
                        for _ in range(5)
                    ],
                    spacing="3",
                    width="100%",
                ),
                background=white(0.02),
                border=f"1px solid {white(0.05)}",
                border_radius="0.5rem",
                padding="0.75rem",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1.25rem",
        width="100%",
        flex="0.6",
        min_width="14rem",
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
                                                rx.badge(
                                                    f"{officer['officer_own_percent']}%",
                                                    color_scheme="gray",
                                                    variant="surface",
                                                    high_contrast=True,
                                                    style={"border_radius": "0.375rem"},
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
                                style={"height": "24.3em"},
                            ),
                            background=white(0.02),
                            border=f"1px solid {white(0.05)}",
                            border_radius="0.5rem",
                            padding="0.75rem",
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
                                    lambda event: rx.box(
                                        rx.hstack(
                                            rx.heading(
                                                event["event_name"],
                                                weight="medium",
                                                size="3",
                                            ),
                                            rx.badge(
                                                f"{event['price_change_ratio']}%",
                                                style={"border_radius": "0.375rem"},
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
                                        border_radius="0.5rem",
                                        padding="0.75rem",
                                        width="100%",
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
                                                rx.badge(
                                                    f"{news['price_change_ratio']}%",
                                                    style={"border_radius": "0.375rem"},
                                                ),
                                            ),
                                            align="center",
                                            justify="between",
                                            width="100%",
                                        ),
                                        background=white(0.02),
                                        border=f"1px solid {white(0.05)}",
                                        border_radius="0.5rem",
                                        padding="0.75rem",
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
            background=white(0.025),
            border=CARD_BORDER,
            border_radius=_CARD_RADIUS,
            padding="1.25rem",
            width="100%",
            flex="0.6",
            min_width="14rem",
            max_width="20em",
            style={"height": "100%"},
        ),
    )
