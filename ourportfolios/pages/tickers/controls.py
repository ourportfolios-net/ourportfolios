"""Controls, filters, and compare toolbar for the tickers page."""

from typing import cast

import reflex as rx

from ourportfolios.components.category_toggle_card import category_toggle_card
from ourportfolios.pages.tickers.state import TickersPageState
from ourportfolios.state import SearchBarState
from ourportfolios.styles import (
    BTN_GHOST_SM,
    BTN_SECONDARY,
    CHIP_STYLE,
    LABEL_STYLE,
    MODAL_BG,
    MODAL_PANEL_STYLE,
    SEARCH_ICON_STYLE,
    SEARCH_INPUT_STYLE,
    TEXT_PURPLE,
    purple,
    white,
)

# ── Filter sliders ─────────────────────────────────────────────────────────────


def _metric_slider(metric_tag: str, option: str) -> rx.Component:
    is_fundamental: bool = option == "F"

    current_value = (
        TickersPageState.fundamentals_current_value[metric_tag]
        if is_fundamental
        else TickersPageState.technicals_current_value[metric_tag]
    )

    default_max = cast(
        "float",
        TickersPageState.fundamentals_default_value[metric_tag][1]
        if is_fundamental
        else TickersPageState.technicals_default_value[metric_tag][1],
    )
    default_step = default_max / 100

    # minWidth:0 is critical — CSS Grid children default to min-width:auto
    # which lets them expand past the column boundary. This fixes overflow.
    return rx.vstack(
        rx.hstack(
            rx.text(
                metric_tag,
                style={
                    **LABEL_STYLE,
                    "font_size": "0.6875rem",
                    "color": white(0.5),
                    "white_space": "nowrap",
                    "text_transform": "uppercase",
                    "overflow": "hidden",
                    "text_overflow": "ellipsis",
                    "flex": "1",
                    "min_width": "0",
                    "letter_spacing": "0.04em",
                },
            ),
            rx.text(
                current_value[0],
                " - ",
                current_value[1],
                style={
                    "font_size": "0.6875rem",
                    "color": white(0.4),
                    "font_weight": "500",
                    "white_space": "nowrap",
                    "flex_shrink": "0",
                },
            ),
            width="100%",
            align="center",
            spacing="2",
            overflow="hidden",
        ),
        rx.slider(
            default_value=current_value,
            on_change=(
                lambda value_range: (
                    TickersPageState.update_fundamental_value(
                        metric=metric_tag,
                        value=value_range,
                    )
                    if is_fundamental
                    else TickersPageState.update_technical_value(
                        metric=metric_tag,
                        value=value_range,
                    )
                )
            ),
            on_value_commit=(
                lambda value_range: (
                    TickersPageState.set_fundamental_metric(
                        metric=metric_tag,
                        value=value_range,
                    )
                    if is_fundamental
                    else TickersPageState.set_technical_metric(
                        metric=metric_tag,
                        value=value_range,
                    )
                )
            ),
            key=f"slider_{option}_{TickersPageState.slider_reset_key}",
            min_=0.0,
            max=default_max,
            step=default_step,
            variant="surface",
            size="2",
            radius="full",
            width="100%",
        ),
        width="100%",
        spacing="2",
        padding="0.5em 0.7em",
        border_radius="0.5rem",
        background=white(0.025),
        border=f"1px solid {white(0.06)}",
        # minWidth:0 stops grid items expanding past column width.
        # clip:hidden clips the Radix thumb that extends slightly beyond the track.
        style={
            "minWidth": "0",
            "boxSizing": "border-box",
            "overflow": "hidden",
            "contain": "layout",
        },
    )


def _metrics_filter(option: str = "F") -> rx.Component:
    keys = rx.cond(
        option == "F",
        TickersPageState.fundamentals_default_value.keys(),
        TickersPageState.technicals_default_value.keys(),
    )
    # Use minmax(0, 1fr) columns — unlike 1fr, minmax(0,1fr) allows grid items
    # to shrink below their content size, preventing horizontal overflow.
    return rx.box(
        rx.foreach(keys, lambda metric_tag: _metric_slider(metric_tag, option)),
        style={
            "display": "grid",
            "gridTemplateColumns": rx.breakpoints(
                initial="minmax(0, 1fr)",
                sm="repeat(2, minmax(0, 1fr))",
                md="repeat(3, minmax(0, 1fr))",
                lg="repeat(4, minmax(0, 1fr))",
            ),
            "gap": "0.45em",
            "width": "100%",
            "boxSizing": "border-box",
            "overflow": "hidden",
        },
        padding=rx.breakpoints(initial="0.6em", sm="0.85em"),
        width="100%",
    )


def _categorical_filter() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text("EXCHANGE", style={**LABEL_STYLE, "font_size": "0.75rem"}),
            rx.flex(
                rx.foreach(
                    TickersPageState.exchange_filter.items(),
                    lambda item: rx.checkbox(
                        item[0],
                        checked=item[1],
                        on_change=lambda value: TickersPageState.set_exchange(
                            exchange=item[0],
                            value=value,
                        ),
                        size="2",
                        color_scheme="violet",
                    ),
                ),
                gap="0.85em",
                wrap="wrap",
            ),
            spacing="2",
        ),
        rx.vstack(
            rx.text("INDUSTRY", style={**LABEL_STYLE, "font_size": "0.75rem"}),
            rx.box(
                rx.flex(
                    rx.foreach(
                        TickersPageState.industry_filter.items(),
                        lambda item: rx.checkbox(
                            item[0],
                            checked=item[1],
                            on_change=lambda value: TickersPageState.set_industry(
                                industry=item[0],
                                value=value,
                            ),
                            size="2",
                            color_scheme="violet",
                        ),
                    ),
                    gap="0.85em",
                    wrap="wrap",
                ),
                height="10em",
                overflow_y="auto",
                overflow_x="hidden",
                width="100%",
            ),
            spacing="2",
        ),
        padding=rx.breakpoints(initial="0.6em", sm="0.85em"),
        spacing="4",
        width="100%",
    )


# ── Filter tab structure ───────────────────────────────────────────────────────


def _filter_tab_panel(option: str, value: str) -> rx.Component:
    body = _categorical_filter() if option == "C" else _metrics_filter(option=option)
    return rx.tabs.content(
        body,
        value=value,
        style={"overflow": "hidden"},
    )


def _filter_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.hstack(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Fundamental",
                    value="fundamental",
                    style={
                        "fontSize": rx.breakpoints(initial="0.72rem", sm="0.8125rem"),
                        "padding": "0 0.5em",
                    },
                ),
                rx.tabs.trigger(
                    "Categorical",
                    value="categorical",
                    style={
                        "fontSize": rx.breakpoints(initial="0.72rem", sm="0.8125rem"),
                        "padding": "0 0.5em",
                    },
                ),
                rx.tabs.trigger(
                    "Technical",
                    value="technical",
                    style={
                        "fontSize": rx.breakpoints(initial="0.72rem", sm="0.8125rem"),
                        "padding": "0 0.5em",
                    },
                ),
                style={"flexShrink": "1", "minWidth": "0", "overflow": "hidden"},
            ),
            rx.button(
                rx.hstack(
                    rx.icon("filter-x", size=11),
                    rx.text("Clear", style={"fontSize": "0.72rem"}),
                    spacing="1",
                    align="center",
                ),
                on_click=TickersPageState.clear_all_filters,
                size="1",
                style=BTN_GHOST_SM,
                flex_shrink="0",
            ),
            width="100%",
            align="center",
            justify="between",
            padding_x="0.65em",
            padding_top="0.4em",
            padding_bottom="0",
            flex_shrink="0",
            overflow="hidden",
        ),
        _filter_tab_panel("F", "fundamental"),
        _filter_tab_panel("C", "categorical"),
        _filter_tab_panel("T", "technical"),
        default_value="fundamental",
        width="100%",
    )


# ── Filter button (menu trigger + dropdown) ────────────────────────────────────


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
                flex_shrink="0",
            ),
        ),
        rx.menu.content(
            # Scrollable tab area - stops before the Apply Filters footer
            rx.box(
                _filter_tabs(),
                overflow_y="auto",
                overflow_x="hidden",
                style={
                    "position": "absolute",
                    "top": "0",
                    "left": "0",
                    "right": "0",
                    "bottom": "2.75em",
                },
            ),
            # Apply Filters footer - always visible, solid bg, above scroll content
            rx.box(
                rx.button(
                    "Apply Filters",
                    on_click=TickersPageState.apply_filters,
                    size="2",
                    style=BTN_GHOST_SM,
                ),
                display="flex",
                justify_content="flex-end",
                align_items="center",
                padding_x="0.75em",
                border_top=f"1px solid {white(0.07)}",
                style={
                    "position": "absolute",
                    "bottom": "0",
                    "left": "0",
                    "right": "0",
                    "height": "2.75em",
                    "background": "rgb(13,13,15)",
                    "zIndex": "10",
                },
            ),
            width=rx.breakpoints(
                initial="min(96vw, 22em)",
                sm="34em",
                md="44em",
                lg="56em",
            ),
            height=rx.breakpoints(
                initial="min(72vh, 26em)",
                sm="28em",
            ),
            max_height="85vh",
            padding="0",
            style={
                **MODAL_PANEL_STYLE,
                "borderRadius": "0.75rem",
                "overflow": "hidden",
                "position": "relative",
            },
            side="bottom",
            align="end",
        ),
        modal=False,
    )


# ── Active filter chips ────────────────────────────────────────────────────────


def _selected_filter_chip(item: str, filter_name: str) -> rx.Component:
    return rx.hstack(
        rx.text(item, size="1", weight="medium", color=white(0.7)),
        rx.box(
            rx.icon("x", size=10, color=white(0.3)),
            cursor="pointer",
            display="flex",
            align_items="center",
            on_click=TickersPageState.remove_filter_chip(item, filter_name),
        ),
        spacing="2",
        align="center",
        padding="0 0.625rem",
        flex_shrink="0",
        style=CHIP_STYLE,
    )


def _metric_filter_chip(item: list, filter_type: str) -> rx.Component:
    metric = item[0]
    label = item[1]
    return rx.hstack(
        rx.text(
            metric,
            ": ",
            label,
            size="1",
            weight="medium",
            color=white(0.7),
            white_space="nowrap",
        ),
        rx.box(
            rx.icon("x", size=10, color=white(0.3)),
            cursor="pointer",
            display="flex",
            align_items="center",
            on_click=TickersPageState.remove_filter_chip(metric, filter_type),
        ),
        spacing="2",
        align="center",
        padding="0 0.625rem",
        flex_shrink="0",
        style=CHIP_STYLE,
    )


def _active_filter_chips() -> rx.Component:
    return rx.flex(
        rx.foreach(
            TickersPageState.applied_industry,
            lambda item: _selected_filter_chip(item, "industry"),
        ),
        rx.foreach(
            TickersPageState.applied_exchange,
            lambda item: _selected_filter_chip(item, "exchange"),
        ),
        rx.foreach(
            TickersPageState.fundamental_chip_items,
            lambda item: _metric_filter_chip(item, "fundamental"),
        ),
        rx.foreach(
            TickersPageState.technical_chip_items,
            lambda item: _metric_filter_chip(item, "technical"),
        ),
        direction="row",
        wrap="nowrap",
        gap="0.5rem",
        align="center",
        height="2.125rem",
        align_items="center",
    )


# ── Board toolbar ──────────────────────────────────────────────────────────────


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
            flex_shrink="0",
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
                style={"scrollbarWidth": "none", "WebkitOverflowScrolling": "touch"},
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


# ── Compare toolbar ────────────────────────────────────────────────────────────


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
                on_mouse_down=rx.prevent_default,
                on_click=[
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
                    min_width=rx.breakpoints(initial="17.5rem", sm="20rem"),
                ),
                rx.fragment(),
            ),
            position="relative",
            spacing="0",
        ),
    )


# ── Metrics settings dialog ────────────────────────────────────────────────────


def _metric_category_card(category: str) -> rx.Component:
    return category_toggle_card(
        title=category,
        checked=TickersPageState.category_selection_state[category],
        on_change=lambda _checked: TickersPageState.toggle_category(category),
        body=rx.box(
            rx.foreach(
                TickersPageState.all_metrics[category],
                lambda metric: rx.hstack(
                    rx.checkbox(
                        checked=TickersPageState.metric_selection_state[metric],
                        on_change=lambda _checked: TickersPageState.toggle_metric(
                            metric,
                        ),
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
                flex_shrink="0",
            ),
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
                        ),
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
                    style={"height": "65vh"},
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
                    flex_shrink="0",
                ),
                spacing="4",
                width="100%",
                overflow="hidden",
            ),
            width=rx.breakpoints(initial="95vw", md="82vw"),
            max_width="100rem",
            overflow="hidden",
            style={**MODAL_PANEL_STYLE, "overflowX": "hidden"},
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
                    rx.cond(
                        TickersPageState.show_graphs,
                        "Hide Graphs",
                        "Show Graphs",
                    ),
                ),
                spacing="2",
                align="center",
            ),
            on_click=TickersPageState.toggle_graphs,
            size="2",
            style=BTN_SECONDARY,
            flex_shrink="0",
        ),
        _metrics_settings_dialog(),
        flex="1",
        spacing="2",
        align="center",
    )
