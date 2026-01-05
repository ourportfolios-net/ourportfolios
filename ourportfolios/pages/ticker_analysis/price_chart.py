"""Price chart component for the ticker landing page."""

import reflex as rx

from ...components.price_chart import PriceChartState
from .state import State


def price_chart_card():
    """Price chart with skeleton while loading."""
    return rx.card(
        rx.vstack(
            rx.script(
                src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js",
            ),
            rx.script(src="/chart.js"),
            rx.box(
                # Skeleton overlay - shown while loading OR when no price data
                rx.cond(
                    State.is_loading_company
                    | (
                        State.price_data.length() <= 1
                    ),  # Show if loading or insufficient data
                    rx.box(
                        rx.skeleton(
                            height="350px",
                            width="calc(100% - 60px)",  # Leave space for price scale
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
                # Actual chart container
                rx.box(
                    id="price_chart",
                    width="100%",
                    height="100%",
                    # Don't use on_mount - it blocks page load
                    # Instead, trigger from ticker_analysis state
                ),
                width="100%",
                height="350px",
                max_height="350px",
                overflow="hidden",
                position="relative",
            ),
            rx.hstack(
                rx.hstack(
                    rx.foreach(
                        PriceChartState.df_by_interval.keys(),
                        lambda item: rx.button(
                            item,
                            variant=rx.cond(
                                PriceChartState.selected_interval == item,
                                "surface",
                                "soft",
                            ),
                            on_click=PriceChartState.set_interval(item),
                        ),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.button(rx.icon("settings", size=20), variant="ghost")
                        ),
                        rx.menu.content(
                            rx.menu.sub(
                                rx.menu.sub_trigger("MA"),
                                rx.menu.sub_content(
                                    rx.vstack(
                                        rx.foreach(
                                            PriceChartState.selected_ma_period.items(),
                                            lambda item: rx.checkbox(
                                                rx.text(
                                                    f"MA{item[0]}",
                                                    color=PriceChartState.ma_period[
                                                        item[0]
                                                    ],
                                                    weight="medium",
                                                ),
                                                checked=item[1],
                                                on_change=lambda value: PriceChartState.add_ma_period(
                                                    value, item[0]
                                                ),
                                            ),
                                        ),
                                        spacing="3",
                                    )
                                ),
                                modal=False,
                            ),
                            rx.menu.sub(
                                rx.menu.sub_trigger("RSI"),
                                rx.menu.sub_content(
                                    rx.checkbox(
                                        rx.text("RSI14", weight="medium"),
                                        checked=PriceChartState.rsi_line,
                                        on_change=PriceChartState.add_rsi_line,
                                    )
                                ),
                            ),
                        ),
                        modal=False,
                    ),
                    rx.button(
                        rx.icon(
                            rx.cond(
                                PriceChartState.selected_chart == "Candlestick",
                                "chart-candlestick",
                                "chart-spline",
                            ),
                            size=15,
                        ),
                        variant="ghost",
                        on_click=PriceChartState.set_selection,
                    ),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
                justify="between",
            ),
            spacing="0",
            width="100%",
        ),
        flex="1",
        min_width="0",
        width="100%",
        height="fit-content",
    )
