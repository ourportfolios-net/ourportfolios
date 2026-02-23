"""Price chart component for the ticker landing page."""

import reflex as rx

from ...styles import white, purple, CARD_BORDER, TEXT_PURPLE
from ...components.price_chart import PriceChartState
from .state import State

_CARD_RADIUS = "10px"

_BTN_BASE = {
    "background": "transparent",
    "border": f"1px solid {white(0.07)}",
    "border_radius": "8px",
    "color": white(0.5),
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.05),
        "color": white(0.85),
        "border_color": white(0.15),
    },
}

_BTN_ACTIVE = {
    "background": white(0.08),
    "border": f"1px solid {white(0.18)}",
    "border_radius": "8px",
    "color": "white",
    "font_weight": "600",
    "cursor": "pointer",
}


def _ma_toggle(label: str, period_key: str):
    """Single MA toggle pill."""
    return rx.box(
        rx.hstack(
            rx.box(
                width="8px",
                height="8px",
                border_radius="50%",
                background=PriceChartState.ma_period[period_key],
                flex_shrink="0",
            ),
            rx.text(label, size="1", weight="medium"),
            spacing="1",
            align="center",
        ),
        padding="0.25em 0.6em",
        border_radius="6px",
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
        on_click=lambda: PriceChartState.add_ma_period(
            ~PriceChartState.selected_ma_period[period_key], period_key
        ),
    )


def _rsi_toggle():
    return rx.box(
        rx.text("RSI14", size="1", weight="medium"),
        padding="0.25em 0.6em",
        border_radius="6px",
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
        on_click=PriceChartState.add_rsi_line(~PriceChartState.rsi_line),
    )


def _chart_type_toggle():
    return rx.hstack(
        rx.box(
            rx.icon("chart-candlestick", size=14),
            padding="0.25em 0.5em",
            border_radius="6px",
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
            border_radius="6px",
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
        border_radius="8px",
        padding="0.2em 0.3em",
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
                            height="350px",
                            width="calc(100% - 60px)",
                            border_radius="8px",
                        ),
                        position="absolute",
                        width="100%",
                        height="350px",
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
                height="350px",
                max_height="350px",
                overflow="hidden",
                position="relative",
            ),
            # Bottom controls row
            rx.hstack(
                # Left: interval buttons
                rx.hstack(
                    rx.foreach(
                        PriceChartState.df_by_interval.keys(),
                        lambda item: rx.button(
                            item,
                            size="2",
                            on_click=PriceChartState.set_interval(item),
                            style=rx.cond(
                                PriceChartState.selected_interval == item,
                                _BTN_ACTIVE,
                                _BTN_BASE,
                            ),
                        ),
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.spacer(),
                # Right: inline indicator toggles
                rx.hstack(
                    # Divider label
                    rx.text(
                        "Overlays",
                        size="1",
                        color=white(0.25),
                        weight="medium",
                        style={
                            "letter_spacing": "0.06em",
                            "text_transform": "uppercase",
                        },
                    ),
                    rx.box(width="1px", height="16px", background=white(0.08)),
                    # MA toggles — iterate over known keys
                    _ma_toggle("MA20", "20"),
                    _ma_toggle("MA50", "50"),
                    _ma_toggle("MA100", "100"),
                    _ma_toggle("MA200", "200"),
                    rx.box(width="1px", height="16px", background=white(0.08)),
                    _rsi_toggle(),
                    rx.box(width="1px", height="16px", background=white(0.08)),
                    # Chart type toggle
                    _chart_type_toggle(),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
                padding_top="0.5em",
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
