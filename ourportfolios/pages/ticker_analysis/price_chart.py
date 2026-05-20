"""Price chart component for the ticker landing page."""

import reflex as rx

from ourportfolios.components.price_chart import PriceChartState
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.ui.primitives import (
    hstack,
    pill_button,
    skeleton_box,
    spacer,
    vstack,
)
from ourportfolios.ui.theme.colors import TEXT_PURPLE, purple, white
from ourportfolios.ui.theme.surfaces import (
    CARD_BORDER,
    PILL_TOGGLE,
    PILL_TOGGLE_ACTIVE,
    RADIUS_INPUT,
    RADIUS_PILL,
)
from ourportfolios.ui.tokens import TRANS_DEFAULT

_INDICATOR_ACTIVE = {
    **PILL_TOGGLE_ACTIVE,
    "color": "white",
}

_INDICATOR_INACTIVE = {
    **PILL_TOGGLE,
    "_hover": {"background": white(0.06), "color": white(0.7)},
}

_RSI_ACTIVE = {
    "background": purple(0.15),
    "border": f"1px solid {purple(0.4)}",
    "color": TEXT_PURPLE,
    "border_radius": RADIUS_PILL,
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
}

_CHART_TYPE_TOGGLE_WRAPPER = {
    "background": white(0.02),
    "border": f"1px solid {white(0.06)}",
    "border_radius": RADIUS_PILL,
    "padding": "0.2em 0.3em",
}


def _ma_toggle(label: str, period_key: str) -> rx.Component:
    """Single MA toggle pill."""
    return rx.box(
        hstack(
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
        border_radius=RADIUS_PILL,
        cursor="pointer",
        style=rx.cond(
            PriceChartState.selected_ma_period[period_key],
            _INDICATOR_ACTIVE,
            _INDICATOR_INACTIVE,
        ),
        on_click=PriceChartState.toggle_ma_period(period_key),
    )


def _rsi_toggle() -> rx.Component:
    return rx.box(
        rx.text("RSI14", size="1", weight="medium"),
        padding="0.25em 0.6em",
        border_radius=RADIUS_PILL,
        cursor="pointer",
        style=rx.cond(
            PriceChartState.rsi_line,
            _RSI_ACTIVE,
            _INDICATOR_INACTIVE,
        ),
        on_click=PriceChartState.toggle_rsi_line,
    )


def _chart_type_toggle() -> rx.Component:
    return hstack(
        rx.box(
            rx.icon("chart-candlestick", size=14),
            padding="0.25em 0.5em",
            border_radius=RADIUS_PILL,
            cursor="pointer",
            display="flex",
            align_items="center",
            style=rx.cond(
                PriceChartState.selected_chart == "Candlestick",
                _INDICATOR_ACTIVE,
                _INDICATOR_INACTIVE,
            ),
            on_click=PriceChartState.set_selection,
        ),
        rx.box(
            rx.icon("chart-spline", size=14),
            padding="0.25em 0.5em",
            border_radius=RADIUS_PILL,
            cursor="pointer",
            display="flex",
            align_items="center",
            style=rx.cond(
                PriceChartState.selected_chart != "Candlestick",
                _INDICATOR_ACTIVE,
                _INDICATOR_INACTIVE,
            ),
            on_click=PriceChartState.set_selection,
        ),
        spacing="1",
        align="center",
        style=_CHART_TYPE_TOGGLE_WRAPPER,
    )


def _interval_buttons() -> rx.Component:
    return hstack(
        pill_button(
            "1D",
            active=PriceChartState.selected_interval == "1D",
            on_click=PriceChartState.set_interval("1D"),
        ),
        pill_button(
            "1W",
            active=PriceChartState.selected_interval == "1W",
            on_click=PriceChartState.set_interval("1W"),
        ),
        pill_button(
            "1M",
            active=PriceChartState.selected_interval == "1M",
            on_click=PriceChartState.set_interval("1M"),
        ),
        spacing="1",
        align="center",
        flex_shrink="0",
    )


def price_chart_card():
    return rx.box(
        vstack(
            rx.script(
                src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js",
            ),
            rx.script(src="/chart.js"),
            # Chart area
            rx.box(
                rx.cond(
                    State.is_loading_company | (State.price_data.length() <= 1),
                    skeleton_box(
                        height="100%",
                        width="calc(100% - 3.75rem)",
                        radius="0.5rem",
                        position="absolute",
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
                flex=["none", "none", "1"],
                height=["21.875rem", "21.875rem", "100%"],
                min_height="21.875rem",
                overflow="hidden",
                position="relative",
            ),
            # Desktop bottom controls
            hstack(
                _interval_buttons(),
                spacer(),
                # Right: inline indicator toggles
                hstack(
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
            vstack(
                hstack(
                    _interval_buttons(),
                    spacer(),
                    _rsi_toggle(),
                    _chart_type_toggle(),
                    align="center",
                    width="100%",
                ),
                hstack(
                    spacer(),
                    _ma_toggle("MA20", "20"),
                    _ma_toggle("MA50", "50"),
                    _ma_toggle("MA100", "100"),
                    _ma_toggle("MA200", "200"),
                    align="center",
                    spacing="2",
                    width="100%",
                    flex_wrap="wrap",
                    justify="end",
                ),
                width="100%",
                spacing="2",
                padding_top="0.5em",
                display=["flex", "flex", "none"],
            ),
            spacing="0",
            width="100%",
            height="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=RADIUS_INPUT,
        padding="1rem",
        flex=["none", "none", "1"],
        min_width="0",
        width="100%",
        display="flex",
        flex_direction="column",
    )
