"""Controls, filters, and compare toolbar for the tickers page."""

import reflex as rx

from .state import TickersPageState
from ...state import SearchBarState
from ...styles import (
    white,
    purple,
    TEXT_PURPLE,
    LABEL_STYLE,
    BTN_PURPLE_SM,
    BTN_GHOST_SM,
    BTN_GHOST_XS,
)


# ── Shared button styles ──────────────────────────────────────────────────────

_BTN_ICON_SECONDARY = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": "8px",
    "color": white(0.6),
    "font_weight": "500",
    "font_size": "13px",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.09),
        "color": white(0.9),
        "border_color": white(0.18),
    },
}

_BTN_FILTER_ACTIVE = {
    "background": purple(0.18),
    "border": f"1px solid {purple(0.5)}",
    "border_radius": "8px",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "font_size": "13px",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {"background": purple(0.28)},
}


# ── Filter sliders ────────────────────────────────────────────────────────────


def _metric_slider(metric_tag: str, option: str):
    return rx.vstack(
        rx.hstack(
            rx.text(metric_tag.upper(), style={**LABEL_STYLE, "font_size": "10px"}),
            rx.spacer(),
            rx.text(
                rx.cond(
                    option == "F",
                    f"{TickersPageState.fundamentals_current_value[metric_tag][0]} – {TickersPageState.fundamentals_current_value[metric_tag][1]}",
                    f"{TickersPageState.technicals_current_value[metric_tag][0]} – {TickersPageState.technicals_current_value[metric_tag][1]}",
                ),
                size="1",
                color=TEXT_PURPLE,
                weight="medium",
            ),
            width="100%",
            align="center",
        ),
        rx.slider(
            value=rx.cond(
                option == "F",
                TickersPageState.fundamentals_current_value[metric_tag],
                TickersPageState.technicals_current_value[metric_tag],
            ),
            on_change=lambda value_range: rx.cond(
                option == "F",
                TickersPageState.set_fundamental_metric(
                    metric=metric_tag, value=value_range
                ).throttle(50),
                TickersPageState.set_technical_metric(
                    metric=metric_tag, value=value_range
                ).throttle(50),
            ),
            min_=0.00,
            max=rx.cond(
                option == "F",
                TickersPageState.fundamentals_default_value[metric_tag][1],
                TickersPageState.technicals_default_value[metric_tag][1],
            ),
            step=rx.cond(
                option == "F",
                TickersPageState.fundamentals_default_value[metric_tag][1] / 100,
                TickersPageState.technicals_default_value[metric_tag][1] / 100,
            ),
            variant="surface",
            size="1",
            radius="full",
        ),
        width="100%",
        spacing="2",
        padding="0.6em 0.75em",
        border_radius="8px",
        background=white(0.025),
        border=f"1px solid {white(0.07)}",
    )


def _metrics_filter(option: str = "F") -> rx.Component:
    return rx.scroll_area(
        rx.grid(
            rx.foreach(
                rx.cond(
                    option == "F",
                    TickersPageState.fundamentals_default_value.keys(),
                    TickersPageState.technicals_default_value.keys(),
                ),
                lambda metric_tag: _metric_slider(metric_tag, option),
            ),
            columns=rx.breakpoints(xs="1", sm="2", md="3", lg="4"),
            gap="0.6em",
            width="100%",
        ),
        padding="0.75em",
        height="22em",
        scrollbars="vertical",
        type="always",
    )


def _categorical_filter():
    return rx.vstack(
        rx.vstack(
            rx.text("EXCHANGE", style=LABEL_STYLE),
            rx.flex(
                rx.foreach(
                    TickersPageState.exchange_filter.items(),
                    lambda item: rx.checkbox(
                        item[0],
                        checked=item[1],
                        on_change=lambda value: TickersPageState.set_exchange(
                            exchange=item[0], value=value
                        ),
                        size="2",
                        color_scheme="violet",
                    ),
                ),
                gap="0.75em",
                wrap="wrap",
            ),
            spacing="2",
        ),
        rx.vstack(
            rx.text("INDUSTRY", style=LABEL_STYLE),
            rx.scroll_area(
                rx.flex(
                    rx.foreach(
                        TickersPageState.industry_filter.items(),
                        lambda item: rx.checkbox(
                            item[0],
                            checked=item[1],
                            on_change=lambda value: TickersPageState.set_industry(
                                industry=item[0], value=value
                            ),
                            size="2",
                            color_scheme="violet",
                        ),
                    ),
                    gap="0.75em",
                    wrap="wrap",
                ),
                scrollbars="vertical",
                type="hover",
                height="10em",
                width="100%",
            ),
            spacing="2",
        ),
        padding="0.75em",
        spacing="4",
        width="100%",
    )


def _filter_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.hstack(
            rx.tabs.list(
                rx.tabs.trigger("Fundamental", value="fundamental"),
                rx.tabs.trigger("Categorical", value="categorical"),
                rx.tabs.trigger("Technical", value="technical"),
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("filter-x", size=12),
                    rx.text("Clear all"),
                    spacing="1",
                    align="center",
                ),
                on_click=TickersPageState.clear_all_filters,
                size="1",
                style=BTN_GHOST_XS,
            ),
            width="100%",
            align="center",
            padding_x="0.75em",
            padding_top="0.5em",
            padding_bottom="0",
        ),
        rx.tabs.content(_metrics_filter(option="F"), value="fundamental"),
        rx.tabs.content(_categorical_filter(), value="categorical"),
        rx.tabs.content(_metrics_filter(option="T"), value="technical"),
        default_value="fundamental",
        style={"flex": "1", "display": "flex", "flex_direction": "column"},
    )


def _selected_filter_chip(item: str, filter: str) -> rx.Component:
    return rx.badge(
        rx.text(
            rx.cond(
                filter == "fundamental",
                f"{item}: {TickersPageState.fundamentals_current_value.get(item, [0.00, 0.00])[0]}–{TickersPageState.fundamentals_current_value.get(item, [0.00, 0.00])[1]}",
                rx.cond(
                    filter == "technical",
                    f"{item}: {TickersPageState.technicals_current_value.get(item, [0.00, 0.00])[0]}–{TickersPageState.technicals_current_value.get(item, [0.00, 0.00])[1]}",
                    item,
                ),
            ),
            size="1",
            weight="medium",
        ),
        rx.button(
            rx.icon("x", size=9),
            variant="ghost",
            size="1",
            style={
                "padding": "0",
                "min_width": "auto",
                "height": "auto",
                "cursor": "pointer",
            },
            on_click=[
                rx.cond(
                    filter == "industry",
                    TickersPageState.set_industry(item, False),
                    rx.cond(
                        filter == "exchange",
                        TickersPageState.set_exchange(item, False),
                        rx.cond(
                            filter == "fundamental",
                            TickersPageState.set_fundamental_metric(item, [0.00, 0.00]),
                            TickersPageState.set_technical_metric(item, [0.00, 0.00]),
                        ),
                    ),
                ),
                TickersPageState.apply_filters,
            ],
        ),
        variant="soft",
        color_scheme="violet",
        radius="full",
        size="1",
    )


def filter_button() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.icon("sliders-horizontal", size=14),
                    rx.text("Filter"),
                    spacing="2",
                    align="center",
                ),
                size="2",
                style=rx.cond(
                    TickersPageState.has_filter, _BTN_FILTER_ACTIVE, _BTN_ICON_SECONDARY
                ),
            )
        ),
        rx.menu.content(
            rx.flex(
                _filter_tabs(),
                rx.flex(
                    rx.spacer(),
                    rx.button(
                        "Apply filters",
                        on_click=TickersPageState.apply_filters,
                        size="2",
                        style=BTN_PURPLE_SM,
                    ),
                    direction="row",
                    width="100%",
                    padding="0.6em 1em",
                    border_top=f"1px solid {white(0.06)}",
                ),
                direction="column",
                height="100%",
                width="100%",
            ),
            width=rx.breakpoints(
                initial="27em", xs="30em", sm="40em", md="44em", lg="56em"
            ),
            height="30em",
            padding="0",
            style={
                "background": "#111111",
                "border": f"1px solid {white(0.08)}",
                "border_radius": "12px",
            },
            side="bottom",
        ),
        modal=False,
    )


def _sort_button() -> rx.Component:
    asc_icon = rx.icon("arrow-down-a-z", size=14)
    desc_icon = rx.icon("arrow-down-z-a", size=14)
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.cond(
                        TickersPageState.selected_sort_order == "ASC",
                        asc_icon,
                        desc_icon,
                    ),
                    rx.text("Sort"),
                    spacing="2",
                    align="center",
                ),
                size="2",
                style=_BTN_ICON_SECONDARY,
            ),
        ),
        rx.menu.content(
            rx.foreach(
                TickersPageState.sort_options.keys(),
                lambda option: rx.menu.sub(
                    rx.menu.sub_trigger(option),
                    rx.menu.sub_content(
                        rx.foreach(
                            TickersPageState.sort_orders,
                            lambda order: rx.menu.item(
                                rx.hstack(
                                    rx.cond(order == "ASC", asc_icon, desc_icon),
                                    rx.text(order),
                                    spacing="2",
                                    align="center",
                                ),
                                on_click=[
                                    TickersPageState.set_sort_option(option),
                                    TickersPageState.set_sort_order(order),
                                ],
                            ),
                        )
                    ),
                ),
            )
        ),
    )


def _active_filter_chips() -> rx.Component:
    return rx.flex(
        rx.foreach(
            TickersPageState.selected_industry,
            lambda item: _selected_filter_chip(item, "industry"),
        ),
        rx.foreach(
            TickersPageState.selected_exchange,
            lambda item: _selected_filter_chip(item, "exchange"),
        ),
        rx.foreach(
            TickersPageState.selected_fundamental_metric,
            lambda item: _selected_filter_chip(item, "fundamental"),
        ),
        rx.foreach(
            TickersPageState.selected_technical_metric,
            lambda item: _selected_filter_chip(item, "technical"),
        ),
        direction="row",
        wrap="wrap",
        gap="2",
        align="center",
    )


def board_toolbar() -> rx.Component:
    return rx.hstack(
        # Search — matches framework page search style exactly
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
                placeholder="Search for a ticker...",
                value=TickersPageState.search_query,
                on_change=TickersPageState.set_search_query,
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
        # Active chips
        rx.cond(
            TickersPageState.has_filter,
            rx.scroll_area(
                _active_filter_chips(),
                scrollbars="horizontal",
                type="hover",
                height="2.4em",
                max_width="40em",
            ),
            rx.fragment(),
        ),
        rx.spacer(),
        _sort_button(),
        filter_button(),
        spacing="2",
        align="center",
        width="100%",
        flex="1",
    )


# ── Compare toolbar ───────────────────────────────────────────────────────────


def _compare_search_suggestion(ticker_value: dict) -> rx.Component:
    ticker = ticker_value["symbol"].to(str)
    industry = ticker_value["industry"].to(str)
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(ticker, size="2", weight="bold", color="white"),
                rx.text(industry, size="1", color=white(0.4)),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("plus", size=13),
                on_click=TickersPageState.add_ticker_to_compare(ticker),
                size="1",
                style=BTN_PURPLE_SM,
            ),
            align="center",
            width="100%",
        ),
        width="100%",
        padding="0.5em 0.75em",
        border_bottom=f"1px solid {white(0.06)}",
        cursor="pointer",
        style={
            "transition": "background 0.12s ease",
            "_hover": {"background": white(0.04)},
        },
    )


def _compare_search_bar() -> rx.Component:
    return rx.box(
        rx.vstack(
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
                    placeholder="Add tickers to compare...",
                    value=SearchBarState.comparison_search_query,
                    on_change=SearchBarState.set_comparison_query,
                    on_blur=lambda: SearchBarState.set_empty_state_display_suggestions(
                        False
                    ),
                    on_focus=lambda: SearchBarState.set_empty_state_display_suggestions(
                        True
                    ),
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
            rx.cond(
                SearchBarState.empty_state_display_suggestion
                & (SearchBarState.get_comparison_suggest_ticker.length() > 0),
                rx.box(
                    rx.scroll_area(
                        rx.foreach(
                            SearchBarState.get_comparison_suggest_ticker,
                            _compare_search_suggestion,
                        ),
                        scrollbars="vertical",
                        type="scroll",
                        style={"maxHeight": "18em"},
                    ),
                    position="absolute",
                    top="calc(100% + 0.4em)",
                    left="0",
                    z_index="200",
                    border_radius="10px",
                    border=f"1px solid {white(0.08)}",
                    background="#111111",
                    overflow="hidden",
                    box_shadow="0 8px 32px rgba(0,0,0,0.6)",
                    min_width="280px",
                ),
                rx.fragment(),
            ),
            position="relative",
            spacing="0",
        ),
    )


def _metric_category_card(category: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(category, size="2", weight="bold", color=white(0.85)),
                rx.spacer(),
                rx.checkbox(
                    checked=TickersPageState.category_selection_state[category],
                    on_change=lambda: TickersPageState.toggle_category(category),
                    size="2",
                    color_scheme="violet",
                ),
                width="100%",
                align="center",
            ),
            rx.box(height="1px", width="100%", background=white(0.06)),
            rx.vstack(
                rx.foreach(
                    TickersPageState.all_metrics[category],
                    lambda metric: rx.hstack(
                        rx.checkbox(
                            checked=TickersPageState.metric_selection_state[metric],
                            on_change=lambda: TickersPageState.toggle_metric(metric),
                            size="1",
                            color_scheme="violet",
                        ),
                        rx.text(
                            TickersPageState.metric_labels[metric],
                            size="1",
                            color=white(0.5),
                        ),
                        spacing="2",
                        align="center",
                    ),
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="0.75em",
        border_radius="10px",
        background=white(0.025),
        border=f"1px solid {white(0.07)}",
        style={
            "transition": "all 0.15s ease",
            "_hover": {"background": white(0.04), "border_color": white(0.12)},
        },
        width="100%",
    )


def _metrics_settings_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("settings-2", size=14),
                size="2",
                style=_BTN_ICON_SECONDARY,
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.text("Metric Settings", size="5", weight="bold", color="white"),
                    rx.spacer(),
                    rx.hstack(
                        rx.text(
                            "Quarterly",
                            size="2",
                            color=rx.cond(
                                TickersPageState.time_period == "quarter",
                                TEXT_PURPLE,
                                white(0.4),
                            ),
                        ),
                        rx.switch(
                            checked=TickersPageState.time_period == "year",
                            on_change=TickersPageState.toggle_time_period,
                            size="2",
                            color_scheme="violet",
                        ),
                        rx.text(
                            "Yearly",
                            size="2",
                            color=rx.cond(
                                TickersPageState.time_period == "year",
                                TEXT_PURPLE,
                                white(0.4),
                            ),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("import", size=13),
                            rx.text("Import Cart"),
                            spacing="2",
                        ),
                        on_click=TickersPageState.import_from_cart,
                        size="2",
                        style=BTN_GHOST_SM,
                    ),
                    rx.dialog.close(
                        rx.icon(
                            "x",
                            size=18,
                            style={
                                "cursor": "pointer",
                                "color": white(0.4),
                                "transition": "color 0.15s ease",
                                "_hover": {"color": "white"},
                            },
                        )
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=white(0.06)),
                rx.scroll_area(
                    rx.box(
                        rx.foreach(
                            TickersPageState.all_metrics.keys(),
                            _metric_category_card,
                        ),
                        display="grid",
                        grid_template_columns="repeat(3, 1fr)",
                        gap="0.75em",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"height": "55vh"},
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Select All",
                        on_click=TickersPageState.select_all_metrics,
                        size="2",
                        style=BTN_GHOST_SM,
                    ),
                    rx.button(
                        "Clear All",
                        on_click=TickersPageState.clear_all_metrics,
                        size="2",
                        style=BTN_GHOST_SM,
                    ),
                    spacing="2",
                ),
                spacing="4",
                width="100%",
            ),
            width="75vw",
            max_width="1600px",
            style={
                "background": "#111111",
                "border": f"1px solid {white(0.08)}",
                "border_radius": "14px",
            },
        ),
    )


def compare_toolbar() -> rx.Component:
    return rx.hstack(
        _compare_search_bar(),
        rx.button(
            rx.hstack(
                rx.cond(
                    TickersPageState.show_graphs,
                    rx.icon("eye-off", size=13),
                    rx.icon("eye", size=13),
                ),
                rx.text(
                    rx.cond(TickersPageState.show_graphs, "Hide Graphs", "Show Graphs")
                ),
                spacing="2",
                align="center",
            ),
            on_click=TickersPageState.toggle_graphs,
            size="2",
            style=_BTN_ICON_SECONDARY,
        ),
        _metrics_settings_dialog(),
        flex="1",
        spacing="2",
        align="center",
    )
