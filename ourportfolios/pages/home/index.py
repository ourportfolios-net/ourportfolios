import reflex as rx
from ...state.home_state import HomeState
from .decision_hub import decision_hub_section
from .market_overview import market_overview_section
from .ticker_of_day import ticker_of_the_day_card
from .cart_glance import cart_glance_panel
from ...components.navbar import navbar


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    """Render the home page."""
    return rx.box(
        navbar(),
        rx.box(
            # Main two-column layout
            rx.flex(
                # ── Left Column (73%): Market Overview + Decision Hub Cards ──
                rx.box(
                    rx.vstack(
                        # Market Overview section (large)
                        market_overview_section(),
                        # Decision Hub Cards row
                        rx.box(
                            decision_hub_section(),
                            width="100%",
                        ),
                        spacing="5",
                        width="100%",
                    ),
                    width=rx.breakpoints(initial="100%", lg="73%"),
                ),
                # ── Right Column (27%): Ticker of Day + Comparison Cart ──
                rx.box(
                    rx.vstack(
                        # Ticker of the Day card
                        ticker_of_the_day_card(),
                        # Comparison Cart panel
                        cart_glance_panel(),
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
