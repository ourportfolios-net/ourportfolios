"""Home dashboard section composition."""

from __future__ import annotations

import reflex as rx

from ..components.cart_card import cart_card
from .decision_hub import decision_hub_section
from .market_overview import market_overview_section
from ..components.hub_cards import selected_framework_card
from ..components.ticker_of_day import ticker_of_the_day_card


def page_body() -> rx.Component:
    return rx.flex(
        rx.box(
            rx.vstack(
                market_overview_section(),
                decision_hub_section(),
                spacing="5",
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="74%"),
        ),
        rx.box(
            rx.vstack(
                ticker_of_the_day_card(),
                selected_framework_card(),
                cart_card(),
                spacing=rx.breakpoints(initial="4", lg="5"),
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="24%"),
            margin_top=rx.breakpoints(initial="1.25rem", lg="0"),
        ),
        justify="between",
        align="start",
        width="100%",
        gap=rx.breakpoints(initial="0", lg="2%"),
        direction=rx.breakpoints(initial="column", lg="row"),
    )
