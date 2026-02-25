import reflex as rx
from ...state.home_state import HomeState
from .hub_cards import compare_assets_card, manage_portfolio_card
from .framework_card import select_framework_card, selected_framework_card
from .market_overview import market_overview_section
from .ticker_of_day import ticker_of_the_day_card
from .cart_card import cart_card
from ...components.navbar import navbar


def decision_hub_section():
    return rx.grid(
        select_framework_card(),
        compare_assets_card(),
        manage_portfolio_card(),
        columns=rx.breakpoints(initial="1", md="3", lg="3"),
        gap="1.25rem",
        width="100%",
    )


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                # Left column
                rx.box(
                    rx.vstack(
                        market_overview_section(),
                        decision_hub_section(),
                        spacing="5",
                        width="100%",
                    ),
                    width=rx.breakpoints(initial="100%", lg="73%"),
                ),
                # Right column
                rx.box(
                    rx.vstack(
                        ticker_of_the_day_card(),
                        selected_framework_card(),
                        cart_card(),
                        spacing="5",
                        width="100%",
                    ),
                    width=rx.breakpoints(initial="100%", lg="27%"),
                    margin_top=rx.breakpoints(initial="1.5rem", lg="0"),
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                gap=rx.breakpoints(initial="0", lg="2rem"),
                width="100%",
            ),
            width="85vw",
            margin="0 auto",
            padding_y="2rem",
        ),
        on_unmount=HomeState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
