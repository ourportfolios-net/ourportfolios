"""Ticker landing page."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.breadcrumb import breadcrumb

from .state import State
from .info_cards import name_card, general_info_card
from .price_chart import price_chart_card
from .metrics_card import key_metrics_card
from .company_info import company_generic_info_card


@rx.page(
    route="/tickers/[ticker]",
    on_load=State.on_mount,
)
def index():
    return rx.box(
        rx.fragment(
            navbar(),
            rx.center(
                rx.box(
                    rx.vstack(
                        breadcrumb("/tickers/[ticker]", tail_label=State.ticker),
                        rx.hstack(
                            rx.vstack(
                                name_card(),
                                general_info_card(),
                                spacing="4",
                                align="center",
                                flex="0 0 auto",
                            ),
                            price_chart_card(),
                            spacing="4",
                            width="100%",
                            align="stretch",
                            min_height="28rem",
                            style={"flexWrap": "wrap"},
                        ),
                        rx.hstack(
                            key_metrics_card(),
                            company_generic_info_card(),
                            spacing="4",
                            width="100%",
                            align="stretch",
                            style={"flexWrap": "wrap"},
                        ),
                        spacing="4",
                        width="100%",
                        justify="between",
                        align="start",
                        key=State.render_key,
                    ),
                    width="clamp(70vw, 86vw, 96vw)",
                    max_width="112.5rem",
                    style={"minHeight": "80vh"},
                ),
                width="100%",
                padding="2em",
                padding_top="5em",
                position="relative",
            ),
            drawer_button(),
        ),
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
