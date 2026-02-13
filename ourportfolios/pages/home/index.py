import reflex as rx
from ...state.home_state import HomeState
from .decision_hub import decision_hub_section
from .market_overview import market_overview_section
from .ticker_of_day import ticker_of_the_day_card
from ...components.navbar import navbar


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    """Render the home page."""
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                rx.box(decision_hub_section(), flex="1", padding_right="2.5rem"),
                rx.vstack(
                    rx.box(
                        ticker_of_the_day_card(),
                        width="100%",
                        display="flex",
                        justify_content="center",
                    ),
                    market_overview_section(),
                    spacing="9",
                    width="22%",
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                gap="0",
                width="100%",
                max_width="100%",
                align_items="flex_end",
            ),
            padding_left=["1.5rem", "2rem", "3rem"],
            padding_y="2rem",
        ),
        on_unmount=HomeState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
