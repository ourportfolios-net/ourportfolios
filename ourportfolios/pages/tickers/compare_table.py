"""Compare table — unified horizontally-scrollable grid with sticky ticker column."""

import reflex as rx

from .state import TickersPageState
from ...styles import (
    white,
    purple,
    TOOLTIP_CURSOR,
    TOOLTIP_CONTENT_STYLE,
    TOOLTIP_WRAPPER_STYLE,
    TEXT_TERTIARY,
    TEXT_TRUNCATE,
    TABLE_BG,
)

# ── Layout constants ───────────────────────────────────────────────────────────────────────
_TICKER_W = "11em"
_METRIC_W_GRAPH = "10em"
_METRIC_W_SIMPLE = "6.5em"
_ROW_H_GRAPH = "4.6em"
_ROW_H_SIMPLE = "3.8em"
_HEADER_H = "2.5em"
_CELL_BORDER = f"1px solid {white(0.04)}"
_STICKY_BORDER = f"1px solid {white(0.06)}"
_BOARD_H = "42em"


# ── Sparkline ─────────────────────────────────────────────────────────────────


def _sparkline(stock: dict, metric_key: str, industry: str) -> rx.Component:
    ticker = stock["symbol"].to(str)
    series = TickersPageState.industry_metric_data_map[industry][metric_key]
    return rx.cond(
        series.length() > 0,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key=ticker,
                stroke=purple(0.75),
                fill=purple(0.08),
                stroke_width=1.5,
                type_="monotone",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.x_axis(data_key="period", hide=True),
            rx.recharts.y_axis(hide=True),
            rx.recharts.tooltip(
                cursor=TOOLTIP_CURSOR,
                content_style=TOOLTIP_CONTENT_STYLE,
                wrapper_style=TOOLTIP_WRAPPER_STYLE,
            ),
            data=series,
            width="100%",
            height=34,
            margin={"top": 2, "right": 4, "left": 4, "bottom": 2},
        ),
        rx.box(width="100%", height="2.125rem"),
    )


# ── Metric cell ───────────────────────────────────────────────────────────────


def _metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    ticker = stock["symbol"].to(str)
    is_best = TickersPageState.industry_best_performers[industry][metric_key] == ticker
    row_h = rx.cond(TickersPageState.show_graphs, _ROW_H_GRAPH, _ROW_H_SIMPLE)
    w = rx.cond(TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE)
    return rx.box(
        rx.vstack(
            rx.text(
                stock[metric_key],
                size="1",
                weight=rx.cond(is_best, "bold", "regular"),
                color=rx.cond(is_best, "rgba(52,211,153,0.9)", white(0.6)),
                style={"white_space": "nowrap", "font_size": "0.72rem"},
            ),
            rx.cond(
                TickersPageState.show_graphs,
                _sparkline(stock, metric_key, industry),
                rx.fragment(),
            ),
            spacing="1",
            align="center",
            justify="center",
            width="100%",
        ),
        width=w,
        min_width=w,
        height=row_h,
        padding_x="0.5em",
        border_right=f"1px solid {white(0.04)}",
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


# ── Ticker card cell (sticky) ─────────────────────────────────────────────────


def _ticker_card(stock: dict) -> rx.Component:
    """Card-style sticky symbol cell with hover slide-left animation."""
    row_h = rx.cond(TickersPageState.show_graphs, _ROW_H_GRAPH, _ROW_H_SIMPLE)
    symbol = stock["symbol"].to(str)
    company_name = stock.get("company_name", "").to(str)
    return rx.box(
        rx.box(
            rx.hstack(
                rx.link(
                    rx.vstack(
                        rx.text(
                            symbol,
                            weight="bold",
                            color="white",
                            style={"font_size": "0.9375rem", "line_height": "1"},
                        ),
                        rx.text(
                            company_name,
                            color=TEXT_TERTIARY,
                            style={
                                **TEXT_TRUNCATE,
                                "font_size": "0.625rem",
                                "line_height": "1.3",
                                "max_width": "7em",
                            },
                        ),
                        spacing="1",
                        align="start",
                    ),
                    href=f"/tickers/{symbol}",
                    text_decoration="none",
                    flex="1",
                    min_width="0",
                    overflow="hidden",
                ),
                rx.box(
                    rx.icon(
                        "x",
                        size=14,
                        color=white(0.2),
                        style={
                            "transition": "color 0.15s ease",
                            "_hover": {"color": white(0.9)},
                        },
                    ),
                    cursor="pointer",
                    on_click=TickersPageState.remove_stock_from_compare(symbol),
                    flex_shrink="0",
                    padding="0.125rem",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            background=white(0.04),
            border=f"1px solid {white(0.07)}",
            border_radius="0.5rem",
            padding="0.55em 0.7em",
            width="calc(100% - 1em)",
            transition="all 0.18s ease",
            _hover={
                "background": white(0.07),
                "border_color": white(0.13),
                "transform": "translateX(-0.1875rem)",
                "box_shadow": "0 0.25rem 1rem rgba(0,0,0,0.35)",
            },
        ),
        width=_TICKER_W,
        min_width=_TICKER_W,
        max_width=_TICKER_W,
        height=row_h,
        padding_x="0.5em",
        display="flex",
        align_items="center",
        border_right=_STICKY_BORDER,
        flex_shrink="0",
        position="sticky",
        left="0",
        z_index="2",
        background=TABLE_BG,
    )


# ── Industry divider ──────────────────────────────────────────────────────────


def _industry_row(industry: str) -> rx.Component:
    return rx.box(
        rx.box(
            rx.badge(
                industry,
                variant="soft",
                color_scheme="gray",
                size="2",
                style={
                    "border_radius": "0.3125rem",
                    "font_size": "0.6875rem",
                    "letter_spacing": "0.04em",
                },
            ),
            width=_TICKER_W,
            min_width=_TICKER_W,
            max_width=_TICKER_W,
            height="2em",
            display="flex",
            align_items="center",
            padding_left="0.85em",
            position="sticky",
            left="0",
            z_index="4",
            background=white(0.012),
        ),
        height="2em",
        min_height="2em",
        display="flex",
        align_items="center",
        border_bottom=_CELL_BORDER,
        background=white(0.012),
        width="max-content",
        min_width="100%",
    )


# ── Header metric column ──────────────────────────────────────────────────────


def _header_metric_col(metric_key: str) -> rx.Component:
    w = rx.cond(TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE)
    return rx.box(
        rx.tooltip(
            rx.text(
                TickersPageState.metric_labels[metric_key],
                size="1",
                weight="medium",
                color=white(0.45),
                style={**TEXT_TRUNCATE, "max_width": "100%"},
            ),
            content=TickersPageState.metric_labels[metric_key],
        ),
        width=w,
        min_width=w,
        height=_HEADER_H,
        display="flex",
        align_items="center",
        justify_content="center",
        padding_x="0.5em",
        border_right=_CELL_BORDER,
        border_bottom=_STICKY_BORDER,
        flex_shrink="0",
    )


# ── Skeleton row (shown while a ticker's data is loading) ─────────────────────


def _skeleton_metric_cell() -> rx.Component:
    w = rx.cond(TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE)
    row_h = rx.cond(TickersPageState.show_graphs, _ROW_H_GRAPH, _ROW_H_SIMPLE)
    return rx.box(
        rx.vstack(
            rx.skeleton(
                height="0.75rem",
                width="3rem",
                border_radius="0.25rem",
            ),
            rx.cond(
                TickersPageState.show_graphs,
                rx.skeleton(
                    height="1.75rem",
                    width="80%",
                    border_radius="0.25rem",
                ),
                rx.fragment(),
            ),
            spacing="1",
            align="center",
            justify="center",
            width="100%",
        ),
        width=w,
        min_width=w,
        height=row_h,
        padding_x="0.5em",
        border_right=_CELL_BORDER,
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def _skeleton_row(ticker: str) -> rx.Component:
    """Skeleton placeholder row shown while a ticker's data is loading."""
    row_h = rx.cond(TickersPageState.show_graphs, _ROW_H_GRAPH, _ROW_H_SIMPLE)
    return rx.hstack(
        # Sticky ticker card skeleton
        rx.box(
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.skeleton(
                            height="0.8125rem", width="2.75rem", border_radius="0.25rem"
                        ),
                        rx.skeleton(
                            height="0.5625rem", width="4.25rem", border_radius="0.25rem"
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.box(
                        rx.icon(
                            "x",
                            size=11,
                            color=white(0.2),
                            style={
                                "transition": "color 0.15s ease",
                                "_hover": {"color": "rgba(239,68,68,0.8)"},
                            },
                        ),
                        cursor="pointer",
                        on_click=TickersPageState.remove_stock_from_compare(ticker),
                        flex_shrink="0",
                        padding="0.125rem",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                background=white(0.04),
                border=f"1px solid {white(0.07)}",
                border_radius="0.5rem",
                padding="0.55em 0.7em",
                width="calc(100% - 1em)",
            ),
            width=_TICKER_W,
            min_width=_TICKER_W,
            max_width=_TICKER_W,
            height=row_h,
            padding_x="0.5em",
            display="flex",
            align_items="center",
            border_right=_STICKY_BORDER,
            flex_shrink="0",
            position="sticky",
            left="0",
            z_index="2",
            background=TABLE_BG,
        ),
        # One skeleton cell per selected metric
        rx.foreach(
            TickersPageState.selected_metrics,
            lambda _metric: _skeleton_metric_cell(),
        ),
        spacing="0",
        align="center",
        border_bottom=_CELL_BORDER,
        width="max-content",
        min_width="100%",
        style={"flex_wrap": "nowrap"},
    )


# ── Public alias ──────────────────────────────────────────────────────────────


def stock_metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    return _metric_cell(stock, metric_key, industry)


def compare_table() -> rx.Component:
    return rx.box(
        rx.cond(
            TickersPageState.is_loading_historical,
            rx.box(
                rx.vstack(
                    rx.icon(
                        "loader",
                        size=28,
                        color=purple(0.8),
                        style={"animation": "spin 1s linear infinite"},
                    ),
                    rx.text("Loading data…", size="2", color=white(0.4)),
                    spacing="3",
                    align="center",
                ),
                position="absolute",
                inset="0",
                display="flex",
                align_items="center",
                justify_content="center",
                background="rgba(9,9,9,0.75)",
                z_index="10",
                border_radius="0.8125rem",
            ),
            rx.fragment(),
        ),
        rx.cond(
            TickersPageState.selected_metrics.length() == 0,
            rx.center(
                rx.vstack(
                    rx.icon("table-2", size=26, color=white(0.18)),
                    rx.text(
                        "No metrics selected",
                        size="3",
                        weight="bold",
                        color=white(0.45),
                    ),
                    rx.text(
                        "Click the  ⚙  settings icon in the toolbar to pick metrics.",
                        size="2",
                        color=white(0.28),
                        text_align="center",
                    ),
                    spacing="2",
                    align="center",
                ),
                height="18em",
                width="100%",
            ),
            rx.scroll_area(
                rx.box(
                    # Sticky header
                    rx.hstack(
                        rx.box(
                            rx.text(
                                "Symbol",
                                size="1",
                                weight="medium",
                                color=white(0.45),
                            ),
                            width=_TICKER_W,
                            min_width=_TICKER_W,
                            max_width=_TICKER_W,
                            height=_HEADER_H,
                            display="flex",
                            align_items="center",
                            padding_left="0.85em",
                            border_right=_STICKY_BORDER,
                            border_bottom=_STICKY_BORDER,
                            flex_shrink="0",
                            position="sticky",
                            left="0",
                            z_index="5",
                            background=TABLE_BG,
                        ),
                        rx.foreach(
                            TickersPageState.selected_metrics,
                            _header_metric_col,
                        ),
                        spacing="0",
                        style={"flex_wrap": "nowrap"},
                        width="max-content",
                        min_width="100%",
                        position="sticky",
                        top="0",
                        z_index="6",
                        background=TABLE_BG,
                    ),
                    # Industry groups + rows
                    rx.foreach(
                        TickersPageState.grouped_stocks.items(),
                        lambda item: rx.box(
                            _industry_row(item[0]),
                            rx.foreach(
                                item[1],
                                lambda stock: rx.hstack(
                                    _ticker_card(stock),
                                    rx.foreach(
                                        TickersPageState.selected_metrics,
                                        lambda metric_key: _metric_cell(
                                            stock, metric_key, item[0]
                                        ),
                                    ),
                                    spacing="0",
                                    align="center",
                                    border_bottom=_CELL_BORDER,
                                    width="max-content",
                                    min_width="100%",
                                    style={
                                        "flex_wrap": "nowrap",
                                        "transition": "background 0.1s ease",
                                        "_hover": {"background": white(0.015)},
                                    },
                                ),
                            ),
                        ),
                    ),
                    # Skeleton rows for tickers added but not yet in stocks
                    rx.foreach(
                        TickersPageState.pending_tickers,
                        _skeleton_row,
                    ),
                    width="max-content",
                    min_width="100%",
                    style={"isolation": "isolate"},
                ),
                scrollbars="both",
                type="auto",
                style={"width": "100%", "height": _BOARD_H},
            ),
        ),
        rx.html(
            "<style>@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}</style>"
        ),
        position="relative",
        width="100%",
        border_radius="0.875rem",
        border=f"1px solid {white(0.07)}",
        background=TABLE_BG,
        overflow="hidden",
    )


def empty_compare_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("between_horizontal_start", size=32, color=white(0.2)),
                padding="1.25em",
                border_radius="0.875rem",
                background=white(0.035),
                border=f"1px solid {white(0.07)}",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.vstack(
                rx.text(
                    "No tickers added yet",
                    size="4",
                    weight="bold",
                    color=white(0.7),
                ),
                rx.text(
                    "Use the search bar above to add tickers for comparison.",
                    size="2",
                    color=white(0.3),
                    text_align="center",
                ),
                spacing="1",
                align="center",
            ),
            spacing="4",
            align="center",
        ),
        height="24em",
        width="100%",
        border_radius="0.875rem",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
    )
