"""Controls, filters, and compare toolbar for the tickers page."""

import reflex as rx

from .state import TickersPageState
from ...state import SearchBarState
from ...components.category_toggle_card import category_toggle_card
from ...styles import (
    white,
    purple,
    TEXT_PURPLE,
    LABEL_STYLE,
    BTN_GHOST_SM,
    BTN_SECONDARY,
    CHIP_STYLE,
    SEARCH_ICON_STYLE,
    SEARCH_INPUT_STYLE,
    MODAL_BG,
    MODAL_PANEL_STYLE,
    FLEX_COL_FILL,
)


# ── Filter sliders ────────────────────────────────────────────────────────────


def _metric_slider(metric_tag: str, option: str):
    return rx.vstack(
        rx.hstack(
            rx.text(
                metric_tag.upper(),
                style={
                    **LABEL_STYLE,
                    "font_size": "0.8125rem",
                    "color": white(0.55),
                    "white_space": "nowrap",
                },
            ),
            rx.spacer(),
            rx.text(
                rx.cond(
                    option == "F",
                    f"{TickersPageState.fundamentals_current_value[metric_tag][0]} – {TickersPageState.fundamentals_current_value[metric_tag][1]}",
                    f"{TickersPageState.technicals_current_value[metric_tag][0]} – {TickersPageState.technicals_current_value[metric_tag][1]}",
                ),
                size="2",
                color=white(0.45),
                weight="medium",
                white_space="nowrap",
            ),
            width="100%",
            align="center",
        ),
        rx.slider(
            default_value=rx.cond(
                option == "F",
                TickersPageState.fundamentals_current_value[metric_tag],
                TickersPageState.technicals_current_value[metric_tag],
            ),
            on_change=lambda value_range: rx.cond(
                option == "F",
                TickersPageState.update_fundamental_value(
                    metric=metric_tag, value=value_range
                ),
                TickersPageState.update_technical_value(
                    metric=metric_tag, value=value_range
                ),
            ),
            on_value_commit=lambda value_range: rx.cond(
                option == "F",
                TickersPageState.set_fundamental_metric(
                    metric=metric_tag, value=value_range
                ),
                TickersPageState.set_technical_metric(
                    metric=metric_tag, value=value_range
                ),
            ),
            key=f"{metric_tag}_{TickersPageState.slider_reset_key}",
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
            size="2",
            radius="full",
            width="100%",
        ),
        width="100%",
        spacing="3",
        padding="0.75em 1em",
        border_radius="0.625rem",
        background=white(0.025),
        border=f"1px solid {white(0.07)}",
    )


def _metrics_filter(option: str = "F") -> rx.Component:
    return rx.grid(
        rx.foreach(
            rx.cond(
                option == "F",
                TickersPageState.fundamentals_default_value.keys(),
                TickersPageState.technicals_default_value.keys(),
            ),
            lambda metric_tag: _metric_slider(metric_tag, option),
        ),
        columns=rx.breakpoints(xs="1", sm="2", md="3", lg="4"),
        gap="0.75em",
        width="100%",
        padding="0.85em",
    )


def _categorical_filter():
    return rx.vstack(
        rx.vstack(
            rx.text("EXCHANGE", style={**LABEL_STYLE, "font_size": "0.8125rem"}),
            rx.flex(
                rx.foreach(
                    TickersPageState.exchange_filter.items(),
                    lambda item: rx.checkbox(
                        item[0],
                        checked=item[1],
                        on_change=lambda value: TickersPageState.set_exchange(
                            exchange=item[0], value=value
                        ),
                        size="3",
                        color_scheme="violet",
                        style={"font_size": "0.9375rem"},
                    ),
                ),
                gap="1em",
                wrap="wrap",
            ),
            spacing="3",
        ),
        rx.vstack(
            rx.text("INDUSTRY", style={**LABEL_STYLE, "font_size": "0.8125rem"}),
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
                            size="3",
                            color_scheme="violet",
                            style={"font_size": "0.9375rem"},
                        ),
                    ),
                    gap="1em",
                    wrap="wrap",
                ),
                scrollbars="vertical",
                type="hover",
                height="12em",
                width="100%",
            ),
            spacing="3",
        ),
        padding="0.85em",
        spacing="5",
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
                size="2",
                style=BTN_GHOST_SM,
            ),
            width="100%",
            align="center",
            padding_x="0.75em",
            padding_top="0.5em",
            padding_bottom="0",
            flex_shrink="0",
        ),
        rx.tabs.content(
            _metrics_filter(option="F"),
            value="fundamental",
            style={**FLEX_COL_FILL, "overflow": "hidden"},
        ),
        rx.tabs.content(
            _categorical_filter(),
            value="categorical",
            style={**FLEX_COL_FILL, "overflow": "auto"},
        ),
        rx.tabs.content(
            _metrics_filter(option="T"),
            value="technical",
            style={**FLEX_COL_FILL, "overflow": "hidden"},
        ),
        default_value="fundamental",
        style=FLEX_COL_FILL,
    )


def _selected_filter_chip(item: str, filter: str) -> rx.Component:
    label = rx.cond(
        filter == "fundamental",
        f"{item}: {TickersPageState.fundamentals_current_value.get(item, [0.00, 0.00])[0]}–{TickersPageState.fundamentals_current_value.get(item, [0.00, 0.00])[1]}",
        rx.cond(
            filter == "technical",
            f"{item}: {TickersPageState.technicals_current_value.get(item, [0.00, 0.00])[0]}–{TickersPageState.technicals_current_value.get(item, [0.00, 0.00])[1]}",
            item,
        ),
    )
    return rx.hstack(
        rx.text(label, size="1", weight="medium", color=white(0.7)),
        rx.box(
            rx.icon("x", size=10, color=white(0.3)),
            cursor="pointer",
            display="flex",
            align_items="center",
            on_click=TickersPageState.remove_filter_chip(item, filter),
        ),
        spacing="2",
        align="center",
        padding="0 0.625rem",
        flex_shrink="0",
        style=CHIP_STYLE,
    )


def filter_button() -> rx.Component:
    _active = TickersPageState.has_filter
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.icon("filter", size=14),
                    rx.text("Filter"),
                    spacing="2",
                    align="center",
                ),
                size="2",
                background=rx.cond(_active, purple(0.18), white(0.05)),
                border=rx.cond(
                    _active,
                    f"1px solid {purple(0.5)}",
                    f"1px solid {white(0.1)}",
                ),
                border_radius="0.5rem",
                color=rx.cond(_active, TEXT_PURPLE, white(0.6)),
                font_weight=rx.cond(_active, "600", "500"),
                font_size="0.8125rem",
                cursor="pointer",
                transition="all 0.15s ease",
            )
        ),
        rx.menu.content(
            rx.flex(
                _filter_tabs(),
                direction="column",
                style={**FLEX_COL_FILL, "overflow": "hidden"},
            ),
            rx.button(
                "Apply Filters",
                on_click=TickersPageState.apply_filters,
                size="2",
                style={
                    **BTN_GHOST_SM,
                    "position": "absolute",
                    "bottom": "0.75em",
                    "right": "0.75em",
                },
            ),
            width=rx.breakpoints(
                initial="27em", xs="30em", sm="40em", md="44em", lg="56em"
            ),
            height="30em",
            padding="0",
            style={
                **MODAL_PANEL_STYLE,
                "border_radius": "0.75rem",
                "position": "relative",
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
                style=BTN_SECONDARY,
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
        wrap="nowrap",
        gap="0.5rem",
        align="center",
        height="2.125rem",
        align_items="center",
    )


def board_toolbar() -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon("search", size=14, color=white(0.25), style=SEARCH_ICON_STYLE),
            rx.input(
                placeholder="Search for a ticker...",
                value=TickersPageState.search_query,
                on_change=TickersPageState.set_search_query,
                size="2",
                style=SEARCH_INPUT_STYLE,
            ),
            position="relative",
            display="flex",
            align_items="center",
        ),
        rx.cond(
            TickersPageState.has_filter,
            rx.box(
                _active_filter_chips(),
                max_width="40em",
                overflow_x="auto",
                overflow_y="hidden",
                height="2.125rem",
                display="flex",
                align_items="center",
                flex_shrink="1",
                min_width="0",
            ),
            rx.fragment(),
        ),
        rx.spacer(),
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
                on_mouse_down=[
                    TickersPageState.set_view_mode("compare"),
                    TickersPageState.add_ticker_to_compare(ticker),
                    SearchBarState.clear_comparison_search(),
                ],
                size="1",
                style=BTN_SECONDARY,
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
                rx.icon("search", size=14, color=white(0.25), style=SEARCH_ICON_STYLE),
                rx.input(
                    placeholder="Add tickers to compare...",
                    value=SearchBarState.comparison_search_query,
                    on_change=SearchBarState.set_comparison_query,
                    on_blur=SearchBarState.blur_comparison_search,
                    on_focus=SearchBarState.focus_comparison_search,
                    size="2",
                    style=SEARCH_INPUT_STYLE,
                ),
                position="relative",
                display="flex",
                align_items="center",
            ),
            rx.cond(
                SearchBarState.empty_state_display_suggestion
                & (SearchBarState.comparison_suggestions.length() > 0),
                rx.box(
                    rx.scroll_area(
                        rx.foreach(
                            SearchBarState.comparison_suggestions,
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
                    border_radius="0.625rem",
                    border=f"1px solid {white(0.08)}",
                    background=MODAL_BG,
                    overflow="hidden",
                    box_shadow="0 0.5rem 2rem rgba(0,0,0,0.6)",
                    min_width="17.5rem",
                ),
                rx.fragment(),
            ),
            position="relative",
            spacing="0",
        ),
    )


def _metric_category_card(category: str) -> rx.Component:
    return category_toggle_card(
        title=category,
        checked=TickersPageState.category_selection_state[category],
        on_change=lambda checked: TickersPageState.toggle_category(category),
        body=rx.box(
            rx.foreach(
                TickersPageState.all_metrics[category],
                lambda metric: rx.hstack(
                    rx.checkbox(
                        checked=TickersPageState.metric_selection_state[metric],
                        on_change=lambda checked: TickersPageState.toggle_metric(metric),
                        size="1",
                        color_scheme="violet",
                    ),
                    rx.text(
                        TickersPageState.metric_labels[metric],
                        size="2",
                        color=white(0.65),
                    ),
                    spacing="2",
                    align="center",
                ),
            ),
            display="grid",
            grid_template_columns="1fr 1fr",
            gap="0.45em 1em",
            width="100%",
        ),
    )


def _metrics_settings_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("settings-2", size=14),
                size="2",
                style=BTN_SECONDARY,
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.text("Metric Settings", size="5", weight="bold", color="white"),
                    rx.spacer(),
                    rx.hstack(
                        rx.badge(
                            "Quarterly",
                            color_scheme=rx.cond(
                                TickersPageState.time_period == "quarter",
                                "violet",
                                "gray",
                            ),
                            variant="soft",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        rx.switch(
                            checked=TickersPageState.time_period == "year",
                            on_change=TickersPageState.toggle_time_period,
                            size="2",
                            color_scheme="violet",
                        ),
                        rx.badge(
                            "Yearly",
                            color_scheme=rx.cond(
                                TickersPageState.time_period == "year",
                                "violet",
                                "gray",
                            ),
                            variant="soft",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.box(width="1px", height="1.2em", background=white(0.1)),
                    rx.button(
                        rx.hstack(
                            rx.icon("import", size=13),
                            rx.text("Import Cart"),
                            spacing="2",
                            align="center",
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
                        grid_template_columns="repeat(auto-fill, minmax(min(16rem, 100%), 1fr))",
                        gap="0.65em",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"height": "68vh"},
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
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            width="82vw",
            max_width="100rem",
            style=MODAL_PANEL_STYLE,
        ),
        open=TickersPageState.metrics_dialog_open,
        on_open_change=TickersPageState.handle_metrics_dialog_change,
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
            style=BTN_SECONDARY,
        ),
        _metrics_settings_dialog(),
        flex="1",
        spacing="2",
        align="center",
    )
