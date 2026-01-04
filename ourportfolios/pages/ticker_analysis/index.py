"""Ticker landing page - detailed view of a specific ticker."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.loading import loading_screen

from .state import State
from .info_cards import name_card, general_info_card, company_profile_card
from .price_chart import price_chart_card
from .metrics_card import key_metrics_card
from .company_info import company_generic_info_card


@rx.page(
    route="/analyze/[ticker]",
    on_load=[State.on_mount],  # Keep for compatibility but session created earlier
)
def index():
    return rx.box(
        rx.fragment(
            loading_screen(),
            navbar(),
            rx.box(
                rx.link(
                    rx.hstack(
                        rx.icon("chevron_left", size=22),
                        rx.text("select", margin_top="-2px"),
                        spacing="0",
                    ),
                    href="/select",
                    underline="none",
                ),
                position="fixed",
                justify="center",
                style={"paddingTop": "1em", "paddingLeft": "0.5em"},
                z_index="1",
            ),
            rx.center(
                rx.box(
                    rx.vstack(
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
                        company_profile_card(),
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
        on_unmount=State.on_unmount,
    )
