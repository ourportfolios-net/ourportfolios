"""Price chart component for the ticker landing page."""

import reflex as rx

from ourportfolios.components.price_chart import PriceChartState
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.styles import CARD_BORDER, TEXT_PURPLE, purple, white

_CARD_RADIUS = "0.625rem"
_CHART_MIN_W = "20rem"

_BTN_BASE = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": "0.5rem",
    "color": white(0.6),
    "font_weight": "500",
    "font_size": "0.8125rem",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.08),
        "color": white(0.9),
        "border_color": white(0.15),
    },
}

_BTN_ACTIVE = {
    "background": white(0.09),
    "border": f"1px solid {white(0.18)}",
    "border_radius": "0.5rem",
    "color": white(0.9),
    "font_weight": "600",
    "font_size": "0.8125rem",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
}


def _ma_toggle(label: str, period_key: str) -> rx.Component:
    """Single MA toggle pill."""
    return rx.box(
        rx.hstack(
            rx.box(
                width="0.5rem",
                height="0.5rem",
                border_radius="50%",
                background=PriceChartState.ma_period[period_key],
                flex_shrink="0",
            ),
            rx.text(label, size="1", weight="medium"),
            spacing="1",
            align="center",
        ),
        padding="0.25em 0.6em",
        border_radius="0.375rem",
        cursor="pointer",
        style=rx.cond(
            PriceChartState.selected_ma_period[period_key],
            {
                "background": white(0.1),
                "border": f"1px solid {white(0.18)}",
                "color": "white",
                "transition": "all 0.15s ease",
            },
            {
                "background": white(0.03),
                "border": f"1px solid {white(0.06)}",
                "color": white(0.35),
                "transition": "all 0.15s ease",
                "_hover": {"background": white(0.06), "color": white(0.7)},
            },
        ),
        on_click=PriceChartState.toggle_ma_period(period_key),
    )


def _rsi_toggle() -> rx.Component:
    return rx.box(
        rx.text("RSI14", size="1", weight="medium"),
        padding="0.25em 0.6em",
        border_radius="0.375rem",
        cursor="pointer",
        style=rx.cond(
            PriceChartState.rsi_line,
            {
                "background": purple(0.15),
                "border": f"1px solid {purple(0.4)}",
                "color": TEXT_PURPLE,
                "transition": "all 0.15s ease",
            },
            {
                "background": white(0.03),
                "border": f"1px solid {white(0.06)}",
                "color": white(0.35),
                "transition": "all 0.15s ease",
                "_hover": {"background": white(0.06), "color": white(0.7)},
            },
        ),
        on_click=PriceChartState.toggle_rsi_line,
    )


def _chart_type_toggle() -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon("chart-candlestick", size=14),
            padding="0.25em 0.5em",
            border_radius="0.375rem",
            cursor="pointer",
            display="flex",
            align_items="center",
            style=rx.cond(
                PriceChartState.selected_chart == "Candlestick",
                {
                    "background": white(0.1),
                    "border": f"1px solid {white(0.18)}",
                    "color": "white",
                    "transition": "all 0.15s ease",
                },
                {
                    "background": white(0.03),
                    "border": f"1px solid {white(0.06)}",
                    "color": white(0.35),
                    "transition": "all 0.15s ease",
                    "_hover": {"background": white(0.06), "color": white(0.7)},
                },
            ),
            on_click=PriceChartState.set_selection,
        ),
        rx.box(
            rx.icon("chart-spline", size=14),
            padding="0.25em 0.5em",
            border_radius="0.375rem",
            cursor="pointer",
            display="flex",
            align_items="center",
            style=rx.cond(
                PriceChartState.selected_chart != "Candlestick",
                {
                    "background": white(0.1),
                    "border": f"1px solid {white(0.18)}",
                    "color": "white",
                    "transition": "all 0.15s ease",
                },
                {
                    "background": white(0.03),
                    "border": f"1px solid {white(0.06)}",
                    "color": white(0.35),
                    "transition": "all 0.15s ease",
                    "_hover": {"background": white(0.06), "color": white(0.7)},
                },
            ),
            on_click=PriceChartState.set_selection,
        ),
        spacing="1",
        align="center",
        background=white(0.02),
        border=f"1px solid {white(0.06)}",
        border_radius="0.5rem",
        padding="0.2em 0.3em",
    )


def _interval_buttons() -> rx.Component:
    return rx.hstack(
        rx.button(
            "1D",
            size="2",
            on_click=PriceChartState.set_interval("1D"),
            background=rx.cond(
                PriceChartState.selected_interval == "1D",
                white(0.09),
                white(0.05),
            ),
            border=rx.cond(
                PriceChartState.selected_interval == "1D",
                f"1px solid {white(0.18)}",
                f"1px solid {white(0.1)}",
            ),
            color=rx.cond(
                PriceChartState.selected_interval == "1D",
                white(0.9),
                white(0.6),
            ),
            font_weight=rx.cond(
                PriceChartState.selected_interval == "1D",
                "600",
                "500",
            ),
            font_size="0.8125rem",
            border_radius="0.5rem",
            cursor="pointer",
            transition="all 0.15s ease",
        ),
        rx.button(
            "1W",
            size="2",
            on_click=PriceChartState.set_interval("1W"),
            background=rx.cond(
                PriceChartState.selected_interval == "1W",
                white(0.09),
                white(0.05),
            ),
            border=rx.cond(
                PriceChartState.selected_interval == "1W",
                f"1px solid {white(0.18)}",
                f"1px solid {white(0.1)}",
            ),
            color=rx.cond(
                PriceChartState.selected_interval == "1W",
                white(0.9),
                white(0.6),
            ),
            font_weight=rx.cond(
                PriceChartState.selected_interval == "1W",
                "600",
                "500",
            ),
            font_size="0.8125rem",
            border_radius="0.5rem",
            cursor="pointer",
            transition="all 0.15s ease",
        ),
        rx.button(
            "1M",
            size="2",
            on_click=PriceChartState.set_interval("1M"),
            background=rx.cond(
                PriceChartState.selected_interval == "1M",
                white(0.09),
                white(0.05),
            ),
            border=rx.cond(
                PriceChartState.selected_interval == "1M",
                f"1px solid {white(0.18)}",
                f"1px solid {white(0.1)}",
            ),
            color=rx.cond(
                PriceChartState.selected_interval == "1M",
                white(0.9),
                white(0.6),
            ),
            font_weight=rx.cond(
                PriceChartState.selected_interval == "1M",
                "600",
                "500",
            ),
            font_size="0.8125rem",
            border_radius="0.5rem",
            cursor="pointer",
            transition="all 0.15s ease",
        ),
        spacing="1",
        align="center",
        flex_shrink="0",
    )


def price_chart_card():
    return rx.box(
        rx.vstack(
            rx.script(
                src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js",
            ),
            rx.script(src="/chart.js"),
            # Chart area
            rx.box(
                rx.cond(
                    State.is_loading_company | (State.price_data.length() <= 1),
                    rx.box(
                        rx.skeleton(
                            height="21.875rem",
                            width="calc(100% - 3.75rem)",
                            border_radius="0.5rem",
                        ),
                        position="absolute",
                        width="100%",
                        height="21.875rem",
                        z_index="1",
                        pointer_events="none",
                        top="0",
                        left="0",
                    ),
                ),
                rx.box(
                    id="price_chart",
                    width="100%",
                    height="100%",
                    key=State.render_key,
                ),
                width="100%",
                height="21.875rem",
                max_height="21.875rem",
                overflow="hidden",
                position="relative",
            ),
            # Desktop Bottom controls
            rx.hstack(
                _interval_buttons(),
                rx.spacer(),
                # Right: inline indicator toggles
                rx.hstack(
                    rx.box(width="1px", height="1rem", background=white(0.08)),
                    # MA toggles
                    _ma_toggle("MA20", "20"),
                    _ma_toggle("MA50", "50"),
                    _ma_toggle("MA100", "100"),
                    _ma_toggle("MA200", "200"),
                    rx.box(width="1px", height="1rem", background=white(0.08)),
                    _rsi_toggle(),
                    rx.box(width="1px", height="1rem", background=white(0.08)),
                    # Chart type toggle
                    _chart_type_toggle(),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
                padding_top="0.5em",
                display=["none", "none", "flex"],
            ),
            # Mobile Bottom controls
            rx.vstack(
                rx.hstack(
                    _interval_buttons(),
                    rx.spacer(),
                    _rsi_toggle(),
                    _chart_type_toggle(),
                    align="center",
                    width="100%",
                ),
                rx.hstack(
                    rx.spacer(),
                    _ma_toggle("MA20", "20"),
                    _ma_toggle("MA50", "50"),
                    _ma_toggle("MA100", "100"),
                    _ma_toggle("MA200", "200"),
                    align="center",
                    spacing="2",
                    width="100%",
                    style={"flexWrap": "wrap"},
                    justify="end",
                ),
                width="100%",
                spacing="2",
                padding_top="0.5em",
                display=["flex", "flex", "none"],
            ),
            spacing="0",
            width="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1rem",
        flex="1",
        min_width="0",
        width="100%",
        height="fit-content",
    )
