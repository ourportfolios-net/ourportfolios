"""Ticker landing page."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button

from .state import State
from .info_cards import name_card, general_info_card
from .price_chart import price_chart_card
from .metrics_card import key_metrics_card
from .company_info import company_generic_info_card


def breadcrumb(ticker: str):
    return rx.hstack(
        rx.html(
            "<style>.breadcrumb-home { color: rgba(255,255,255,0.35) !important; text-decoration: none !important; transition: color 0.15s ease; } .breadcrumb-home:hover { color: white !important; }</style>"
        ),
        rx.link(
            "Home",
            href="/home",
            size="2",
            class_name="breadcrumb-home",
        ),
        rx.icon("chevron-right", size=13, color="rgba(255,255,255,0.2)"),
        rx.link(
            "Tickers",
            href="/tickers",
            size="2",
            class_name="breadcrumb-home",
        ),
        rx.icon("chevron-right", size=13, color="rgba(255,255,255,0.2)"),
        rx.text(
            ticker,
            size="2",
            color="rgba(255,255,255,0.75)",
            weight="medium",
        ),
        spacing="2",
        align="center",
        style={"marginBottom": "0.5em"},
    )


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
                        breadcrumb(State.ticker),
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
                            height="450px",
                        ),
                        rx.hstack(
                            key_metrics_card(),
                            company_generic_info_card(),
                            spacing="4",
                            width="100%",
                            align="stretch",
                        ),
                        spacing="4",
                        width="100%",
                        justify="between",
                        align="start",
                        key=State.render_key,
                    ),
                    width="86vw",
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
