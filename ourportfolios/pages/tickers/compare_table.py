"""Compare table — unified horizontally-scrollable grid with sticky ticker column."""

import reflex as rx

from .state import TickersPageState
from ...styles import (
    white,
    purple,
    LABEL_STYLE,
    TOOLTIP_CURSOR,
    TOOLTIP_CONTENT_STYLE,
    TOOLTIP_WRAPPER_STYLE,
    DELETE_HOVER,
)

# ── Layout constants ───────────────────────────────────────────────────────────
_TICKER_W = "10em"
_METRIC_W_GRAPH = "13em"
_METRIC_W_SIMPLE = "7em"
_ROW_H = "3.5em"
_HEADER_H = "3em"
_TABLE_BG = "#111111"
_STICKY_BG = "#111111"  # opaque so sticky cells occlude scrolled content


# ── Sub-components ─────────────────────────────────────────────────────────────


def _sparkline(stock: dict, metric_key: str, industry: str) -> rx.Component:
    ticker = stock["symbol"].to(str)
    series = TickersPageState.industry_metric_data_map[industry][metric_key]
    return rx.cond(
        series.length() > 0,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key=ticker,
                stroke=purple(0.8),
                fill=purple(0.15),
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
            height=44,
            margin={"top": 2, "right": 2, "left": 2, "bottom": 2},
        ),
        rx.box(width="100%", height="44px"),
    )


def _metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    ticker = stock["symbol"].to(str)
    is_best = TickersPageState.industry_best_performers[industry][metric_key] == ticker
    return rx.box(
        rx.vstack(
            rx.text(
                stock[metric_key],
                size="2",
                weight=rx.cond(is_best, "bold", "regular"),
                color=rx.cond(is_best, "rgba(52,211,153,0.95)", white(0.65)),
                style={"white_space": "nowrap"},
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
        width=rx.cond(TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE),
        min_width=rx.cond(
            TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE
        ),
        height=_ROW_H,
        padding_x="0.5em",
        border_right=f"1px solid {white(0.05)}",
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def _ticker_cell(stock: dict) -> rx.Component:
    """Sticky first-column cell: link to ticker page + remove button."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.text(
                    stock["symbol"],
                    weight="bold",
                    size="2",
                    color="white",
                    style={"white_space": "nowrap"},
                ),
                href=f"/tickers/{stock['symbol']}",
                text_decoration="none",
                _hover={"text_decoration": "none", "opacity": "0.8"},
            ),
            rx.spacer(),
            rx.icon(
                "x",
                size=12,
                color=white(0.25),
                cursor="pointer",
                on_click=TickersPageState.remove_stock_from_compare(stock["symbol"]),
                style={
                    "transition": "color 0.15s ease",
                    "_hover": {"color": DELETE_HOVER},
                    "flex_shrink": "0",
                },
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        width=_TICKER_W,
        min_width=_TICKER_W,
        max_width=_TICKER_W,
        height=_ROW_H,
        padding_x="0.75em",
        display="flex",
        align_items="center",
        border_right=f"1px solid {white(0.08)}",
        flex_shrink="0",
        # Sticky magic
        position="sticky",
        left="0",
        z_index="2",
        background=_STICKY_BG,
    )


def _industry_row(industry: str) -> rx.Component:
    """Full-width industry divider row."""
    return rx.box(
        rx.badge(
            industry,
            variant="soft",
            color_scheme="violet",
            size="1",
            style={"border_radius": "6px"},
        ),
        height="2.25em",
        min_height="2.25em",
        display="flex",
        align_items="center",
        padding_left="0.75em",
        border_bottom=f"1px solid {white(0.04)}",
        background=white(0.012),
        position="sticky",
        left="0",
        width="100%",
        min_width="max-content",
    )


def _header_metric_col(metric_key: str) -> rx.Component:
    return rx.box(
        rx.tooltip(
            rx.text(
                TickersPageState.metric_labels[metric_key],
                style={
                    **LABEL_STYLE,
                    "white_space": "nowrap",
                    "overflow": "hidden",
                    "text_overflow": "ellipsis",
                    "max_width": "100%",
                },
            ),
            content=TickersPageState.metric_labels[metric_key],
        ),
        width=rx.cond(TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE),
        min_width=rx.cond(
            TickersPageState.show_graphs, _METRIC_W_GRAPH, _METRIC_W_SIMPLE
        ),
        height=_HEADER_H,
        display="flex",
        align_items="center",
        justify_content="center",
        padding_x="0.5em",
        border_right=f"1px solid {white(0.05)}",
        border_bottom=f"1px solid {white(0.06)}",
        flex_shrink="0",
    )


# ── Public alias (kept for back-compat with any other imports) ─────────────────
def stock_metric_cell(stock: dict, metric_key: str, industry: str) -> rx.Component:
    return _metric_cell(stock, metric_key, industry)


def compare_table() -> rx.Component:
    return rx.box(
        # ── Loading overlay ──────────────────────────────────────────────────
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
                border_radius="13px",
            ),
            rx.fragment(),
        ),
        # ── No-metrics hint ──────────────────────────────────────────────────
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
            # ── Unified scrollable table ──────────────────────────────────────
            rx.scroll_area(
                rx.box(
                    # Sticky header row
                    rx.hstack(
                        rx.box(
                            rx.text(
                                "SYMBOL",
                                style=LABEL_STYLE,
                            ),
                            width=_TICKER_W,
                            min_width=_TICKER_W,
                            max_width=_TICKER_W,
                            height=_HEADER_H,
                            display="flex",
                            align_items="center",
                            padding_left="0.75em",
                            border_right=f"1px solid {white(0.08)}",
                            border_bottom=f"1px solid {white(0.06)}",
                            flex_shrink="0",
                            position="sticky",
                            left="0",
                            z_index="3",
                            background=_STICKY_BG,
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
                        z_index="2",
                        background=_TABLE_BG,
                    ),
                    # Industry groups + rows
                    rx.foreach(
                        TickersPageState.grouped_stocks.items(),
                        lambda item: rx.box(
                            _industry_row(item[0]),
                            rx.foreach(
                                item[1],
                                lambda stock: rx.hstack(
                                    _ticker_cell(stock),
                                    rx.foreach(
                                        TickersPageState.selected_metrics,
                                        lambda metric_key: _metric_cell(
                                            stock, metric_key, item[0]
                                        ),
                                    ),
                                    spacing="0",
                                    align="center",
                                    border_bottom=f"1px solid {white(0.05)}",
                                    width="max-content",
                                    min_width="100%",
                                    style={
                                        "flex_wrap": "nowrap",
                                        "transition": "background 0.12s ease",
                                        "_hover": {"background": white(0.022)},
                                    },
                                ),
                            ),
                        ),
                    ),
                    width="max-content",
                    min_width="100%",
                    style={"isolation": "isolate"},
                ),
                scrollbars="both",
                type="auto",
                style={
                    "width": "100%",
                    "max_height": "calc(100vh - 19em)",
                },
            ),
        ),
        # Spin keyframes
        rx.html(
            "<style>@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}</style>"
        ),
        position="relative",
        width="100%",
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=_TABLE_BG,
        overflow="hidden",
    )


def empty_compare_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon("bar-chart-2", size=32, color=white(0.2)),
                padding="1.25em",
                border_radius="14px",
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
        border_radius="14px",
        border=f"1px solid {white(0.07)}",
        background=white(0.025),
    )
