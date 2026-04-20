"""Ticker landing page."""

import reflex as rx

from ourportfolios.components.breadcrumb import breadcrumb
from ourportfolios.components.drawer import drawer_button
from ourportfolios.components.navbar import navbar
from ourportfolios.pages.ticker_analysis.company_info import company_generic_info_card
from ourportfolios.pages.ticker_analysis.info_cards import general_info_card, name_card
from ourportfolios.pages.ticker_analysis.metrics_card import key_metrics_card
from ourportfolios.pages.ticker_analysis.price_chart import price_chart_card
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.state.auth_state import AuthState


def _desktop_layout() -> rx.Component:
    """Two-column layout shown on md+ screens."""
    return rx.vstack(
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
        display=["none", "none", "flex"],
    )


def _mobile_layout() -> rx.Component:
    """Single-column layout shown on xs/sm screens."""
    return rx.vstack(
        name_card(),
        price_chart_card(),
        key_metrics_card(),
        company_generic_info_card(),
        spacing="4",
        width="100%",
        align="stretch",
        display=["flex", "flex", "none"],
    )


@rx.page(
    route="/tickers/[ticker]",
    on_load=[State.on_mount, AuthState.check_auth_status, State.auto_load_data],
)
def index() -> rx.Component:
    return rx.box(
        rx.fragment(
            navbar(),
            rx.center(
                rx.box(
                    rx.vstack(
                        breadcrumb("/tickers/[ticker]", tail_label=State.ticker),
                        _desktop_layout(),
                        _mobile_layout(),
                        spacing="4",
                        width="100%",
                        key=State.render_key,
                    ),
                    width="86vw",
                    max_width="90rem",
                    style={"minHeight": "80vh"},
                ),
                width="100%",
                padding=["1em", "1.5em", "2em"],
                padding_top=["4em", "4.5em", "5em"],
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
