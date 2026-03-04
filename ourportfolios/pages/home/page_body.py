import reflex as rx
from .market_overview import market_overview_section
from .ticker_of_day import ticker_of_the_day_card
from .framework_card import selected_framework_card
from .cart_card import cart_card
from .decision_hub import decision_hub_section


def page_body() -> rx.Component:
    return rx.flex(
        # Left column — 75%
        rx.box(
            rx.vstack(
                market_overview_section(),
                decision_hub_section(),
                spacing="5",
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="75%"),
        ),
        # Right column — 25%
        rx.box(
            rx.vstack(
                ticker_of_the_day_card(),
                selected_framework_card(),
                cart_card(),
                spacing="5",
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="25%"),
            margin_top=rx.breakpoints(initial="1.5rem", lg="0"),
        ),
        direction=rx.breakpoints(initial="column", lg="row"),
        gap=rx.breakpoints(initial="0", lg="2rem"),
        width="100%",
    )
