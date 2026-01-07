"""Filter components for the select page."""

import reflex as rx

from .state import State


def metric_slider(metric_tag: str, option: str):
    return rx.vstack(
        # Metric
        rx.hstack(
            rx.badge(
                rx.text(
                    metric_tag.capitalize(),
                    font_size="lg",
                    font_weight="medium",
                    size="2",
                ),
                variant="soft",
                radius="small",
                color_scheme="violet",
            ),
            # Current value range
            rx.badge(
                rx.cond(
                    option == "F",
                    f"{State.fundamentals_current_value[metric_tag][0]} - {State.fundamentals_current_value[metric_tag][1]}",
                    f"{State.technicals_current_value[metric_tag][0]} - {State.technicals_current_value[metric_tag][1]}",
                ),
                radius="small",
                variant="solid",
                color_scheme="violet",
            ),
        ),
        rx.slider(
            value=rx.cond(
                option == "F",
                State.fundamentals_current_value[metric_tag],
                State.technicals_current_value[metric_tag],
            ),
            on_change=lambda value_range: rx.cond(
                option == "F",
                State.set_fundamental_metric(
                    metric=metric_tag, value=value_range
                ).throttle(50),
                State.set_technical_metric(
                    metric=metric_tag, value=value_range
                ).throttle(50),
            ),
            min_=0.00,
            max=rx.cond(
                option == "F",
                State.fundamentals_default_value[metric_tag][1],
                State.technicals_default_value[metric_tag][1],
            ),
            step=rx.cond(
                option == "F",
                State.fundamentals_default_value[metric_tag][1] / 100,
                State.technicals_default_value[metric_tag][1] / 100,
            ),
            variant="surface",
            size="2",
            radius="full",
            orientation="horizontal",
        ),
        width="90%",
        align="start",
        padding="1em",
    )


def metrics_filter(option: str = "F") -> rx.Component:
    """Reusable slider section for both fundamentals & technicals
    option(str): {"F": for Fundamental-metrics,
                   "T" for Technical-metrics}
    """
    return rx.scroll_area(
        rx.grid(
            rx.foreach(
                rx.cond(
                    option == "F",
                    State.fundamentals_default_value.keys(),
                    State.technicals_default_value.keys(),
                ),
                lambda metric_tag: metric_slider(metric_tag, option),
            ),
            columns=rx.breakpoints(
                xs="1",
                sm="2",
                md="3",
                lg="4",
            ),
            spacing="2",
            flow="row",
            wrap="wrap",
            align="center",
        ),
        paddingTop="1.5em",
        paddingRight="0.5em",
        height="22em",
        scrollbars="vertical",
        type="always",
    )


def categorical_filter():
    grid_layout = {
        "columns": rx.breakpoints(
            initial="1",
            xs="2",
            sm="3",
            md="3",
            lg="4",
        ),
        "spacing": "4",
        "flow": "row",
        "align": "center",
        "paddingLeft": "0.5em",
        "paddingRight": "1em",
        "justify": "between",
        "wrap": "wrap",
    }

    return rx.vstack(
        # Exchange
        rx.vstack(
            rx.heading("Exchange", size="6"),
            rx.center(
                rx.grid(
                    rx.foreach(
                        State.exchange_filter.items(),
                        lambda item: rx.checkbox(
                            rx.badge(item[0]),
                            checked=item[1],
                            on_change=lambda value: State.set_exchange(
                                exchange=item[0], value=value
                            ),
                        ),
                    ),
                    **grid_layout,
                ),
                width="100%",
            ),
            spacing="2",
        ),
        # Industry
        rx.vstack(
            rx.heading("Industry", size="6"),
            rx.scroll_area(
                rx.grid(
                    rx.foreach(
                        State.industry_filter.items(),
                        lambda item: rx.checkbox(
                            rx.badge(item[0]),
                            checked=item[1],
                            on_change=lambda value: State.set_industry(
                                industry=item[0], value=value
                            ),
                            size="1",
                        ),
                    ),
                    **grid_layout,
                ),
                scrollbar="vertical",
                type="hover",
                width="100%",
                height="12em",
            ),
            spacing="2",
        ),
        paddingTop="2em",
        paddingLeft="0.5em",
        spacing="6",
        width="100%",
    )


def filter_tabs() -> rx.Component:
    return (
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Fundamental", value="fundamental"),
                rx.tabs.trigger("Categorical", value="categorical"),
                rx.tabs.trigger("Technical", value="technical"),
                rx.spacer(),
                rx.flex(
                    # Clear filter
                    rx.button(
                        rx.hstack(
                            rx.icon("filter-x", size=12),
                            rx.text("Clear all"),
                            align="center",
                        ),
                        variant="outline",
                        on_click=State.clear_all_filters,
                    ),
                    align="center",
                    direction="row",
                    spacing="2",
                ),
            ),
            rx.tabs.content(
                metrics_filter(option="F"),
                value="fundamental",
            ),
            rx.tabs.content(
                categorical_filter(),
                value="categorical",
            ),
            rx.tabs.content(
                metrics_filter(option="T"),
                value="technical",
            ),
            default_value="fundamental",
            style={"flex": "1"},
        ),
    )


def selected_filter_chip(item: str, filter: str) -> rx.Component:
    return rx.badge(
        rx.text(
            rx.cond(
                filter == "fundamental",
                f"{item}: {State.fundamentals_current_value.get(item, [0.00, 0.00])[0]}-{State.fundamentals_current_value.get(item, [0.00, 0.00])[1]}",
                rx.cond(
                    filter == "technical",
                    f"{item}: {State.technicals_current_value.get(item, [0.00, 0.00])[0]}-{State.technicals_current_value.get(item, [0.00, 0.00])[1]}",
                    item,
                ),
            ),
            size="2",
            weight="medium",
        ),
        rx.button(
            rx.icon("circle-x", size=11),
            variant="ghost",
            on_click=[
                rx.cond(
                    filter == "industry",
                    State.set_industry(item, False),
                    rx.cond(
                        filter == "exchange",
                        State.set_exchange(item, False),
                        rx.cond(
                            filter == "fundamental",
                            State.set_fundamental_metric(item, [0.00, 0.00]),
                            State.set_technical_metric(item, [0.00, 0.00]),
                        ),
                    ),
                ),
                State.apply_filters,
            ],
        ),
        color_scheme="violet",
        radius="large",
        variant="outline",
        _hover={"opacity": 0.75},
        size="2",
    )


def display_selected_filter() -> rx.Component:
    return rx.flex(
        rx.foreach(
            State.selected_industry, lambda item: selected_filter_chip(item, "industry")
        ),
        rx.foreach(
            State.selected_exchange, lambda item: selected_filter_chip(item, "exchange")
        ),
        rx.foreach(
            State.selected_fundamental_metric,
            lambda item: selected_filter_chip(item, "fundamental"),
        ),
        rx.foreach(
            State.selected_technical_metric,
            lambda item: selected_filter_chip(item, "technical"),
        ),
        direction="row",
        spacing="2",
        align="center",
        justify="start",
    )


def filter_button() -> rx.Component:
    return (
        rx.menu.root(
            rx.menu.trigger(
                rx.button(
                    rx.hstack(
                        rx.icon("filter", size=12),
                        rx.text("Filter"),
                        align="center",
                    ),
                    variant=rx.cond(State.has_filter, "solid", "outline"),
                )
            ),
            rx.menu.content(
                rx.flex(
                    filter_tabs(),
                    # Apply button - fixed at bottom right
                    rx.flex(
                        rx.spacer(),
                        rx.button(
                            rx.text("Apply", weight="medium", color="white", size="2"),
                            variant="solid",
                            on_click=State.apply_filters,
                        ),
                        direction="row",
                        width="100%",
                        padding_right="1em",
                        padding_bottom="0.5em",
                    ),
                    direction="column",
                    height="100%",
                    width="100%",
                ),
                width=rx.breakpoints(
                    initial="27em", xs="30em", sm="40em", md="40em", lg="52em"
                ),
                height="28em",
                side="left",
            ),
            modal=False,
        ),
    )
