"""Reusable mini index/metric card with sparkline chart.

Usage:
    mini_chart_card(
        label="VNIndex",
        value=HomeState.vnindex_value,
        abs_change=HomeState.vnindex_change,
        pct_change=HomeState.vnindex_pct_change,
        is_positive=HomeState.vnindex_is_positive,
        chart_data=HomeState.vnindex_chart_data,
        data_key="normalized_close",
    )
"""

from dataclasses import dataclass

import reflex as rx

from ourportfolios.styles import CARD_BG, CARD_BORDER, TEXT_TERTIARY, purple

_CHART_W = 80
_CHART_H = 52

_SHELL = {
    "padding": "0.625rem 0.875rem",
    "border_radius": "0.625rem",
    "background": CARD_BG,
    "border": CARD_BORDER,
    "box_sizing": "border-box",
}


@dataclass(slots=True)
class MiniChartCardProps:
    label: str
    value: str
    abs_change: str
    pct_change: str
    is_positive: bool
    chart_data: list[dict[str, float | str]]
    chart_w: int = _CHART_W
    chart_h: int = _CHART_H
    stroke_color_pos: str | None = None
    fill_color_pos: str | None = None


def _skel(w: str, h: str, r: str = "0.375rem") -> rx.Component:
    return rx.skeleton(rx.box(width=w, height=h), loading=True, border_radius=r)


def mini_chart_card(
    card: MiniChartCardProps,
    data_key: str = "normalized_close",
) -> rx.Component:
    """Reusable mini sparkline card.

    Args:
        card:              Card props and chart data.
        data_key:          Key in chart_data dicts to plot (default "normalized_close").
        card.chart_w:      Sparkline width in px.
        card.chart_h:      Sparkline height in px.
        card.stroke_color_pos: Stroke color when positive (defaults to purple).
        card.fill_color_pos: Fill color when positive (defaults to purple).

    """
    stroke_pos = card.stroke_color_pos or purple(0.85)
    fill_pos = card.fill_color_pos or purple(0.12)

    badge_scheme = rx.cond(card.is_positive, "green", "red")

    chart = rx.box(
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key=data_key,
                stroke=stroke_pos,
                fill=fill_pos,
                stroke_width=2.2,
                width="100%",
                active_dot={"r": 4, "strokeWidth": 0},
                is_animation_active=False,
            ),
            rx.recharts.x_axis(data_key="name", hide=True),
            rx.recharts.y_axis(domain=[0, 1], hide=True),
            data=card.chart_data,
            width=card.chart_w,
            height=card.chart_h,
        ),
        width=f"{card.chart_w}px",
        height=f"{card.chart_h}px",
        flex_shrink="0",
        overflow="hidden",
    )

    loaded = (
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(card.label, size="1", weight="medium", color=TEXT_TERTIARY),
                    rx.text(card.value, size="5", weight="bold", color="white"),
                    rx.hstack(
                        rx.badge(
                            card.abs_change,
                            color_scheme=badge_scheme,
                            variant="soft",
                            size="1",
                        ),
                        rx.badge(
                            card.pct_change,
                            color_scheme=badge_scheme,
                            variant="soft",
                            size="1",
                        ),
                        spacing="1",
                    ),
                    spacing="0",
                    align="start",
                ),
                chart,
                align="center",
                justify="between",
                width="100%",
                spacing="0",
            ),
            style=_SHELL,
        ),
    )

    skeleton = rx.box(
        rx.hstack(
            rx.vstack(
                _skel("3.25rem", "0.625rem"),
                _skel("5.5rem", "1.5rem", "0.375rem"),
                rx.hstack(
                    _skel("3rem", "1rem", "0.5rem"),
                    _skel("3.5rem", "1rem", "0.5rem"),
                    spacing="1",
                ),
                spacing="1",
            ),
            rx.spacer(),
            _skel(f"{card.chart_w}px", f"{card.chart_h}px", "0.375rem"),
            align="center",
            width="100%",
        ),
        style=_SHELL,
    )

    return rx.cond(card.value, loaded, skeleton)
