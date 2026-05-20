"""Ticker landing page."""

import reflex as rx

from ourportfolios.components.breadcrumb import breadcrumb
from ourportfolios.components.drawer import drawer_button
from ourportfolios.components.navbar import navbar
from ourportfolios.pages.ticker_analysis.company_info import company_generic_info_card
from ourportfolios.pages.ticker_analysis.dialog import company_profile_dialog
from ourportfolios.pages.ticker_analysis.info_cards import general_info_card, name_card
from ourportfolios.pages.ticker_analysis.metrics_card import key_metrics_card
from ourportfolios.pages.ticker_analysis.price_chart import price_chart_card
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.state.auth_state import AuthState

_DESKTOP_DETAIL_ROW_HEIGHT = "52rem"


def _desktop_layout() -> rx.Component:
    return rx.vstack(
        rx.box(
            # Left column — fixed width, stretches to row height set by chart
            rx.box(
                name_card(),
                general_info_card(),
                rx.box(company_profile_dialog(), flex_shrink="0"),
                display="flex",
                flex_direction="column",
                gap="1rem",
                align_self="stretch",
                overflow="hidden",
                width="17rem",
                min_width="17rem",
                max_width="20rem",
                flex_shrink="0",
            ),
            # Right column — price chart directly, drives row height
            price_chart_card(),
            display="flex",
            flex_direction="row",
            align_items="stretch",
            gap="1rem",
            width="100%",
            flex_shrink="0",
        ),
        rx.hstack(
            key_metrics_card(),
            company_generic_info_card(),
            spacing="4",
            width="100%",
            align="stretch",
            flex_shrink="0",
            height=_DESKTOP_DETAIL_ROW_HEIGHT,
            min_height=_DESKTOP_DETAIL_ROW_HEIGHT,
            max_height=_DESKTOP_DETAIL_ROW_HEIGHT,
            overflow="hidden",
        ),
        spacing="8",
        width="100%",
        align="start",
        display=["none", "none", "flex"],
    )


def _mobile_layout() -> rx.Component:
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
                    min_height=[
                        "calc(100vh - 5em)",
                        "calc(100vh - 6em)",
                        "calc(100vh - 7em)",
                    ],
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
