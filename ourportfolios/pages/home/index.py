import reflex as rx
from ...state.home_state import HomeState
from .decision_hub import decision_hub_section
from .market_overview import market_overview_section
from ...components.navbar import navbar


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    """Render the home page."""
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                rx.box(decision_hub_section(), flex="1"),
                rx.box(market_overview_section(), width="20%"),
                direction=rx.breakpoints(initial="column", lg="row"),
                gap="1.5rem",
                width="100%",
                max_width="1440px",
                margin="0 auto",
                align_items="flex_end",
            ),
            padding_x=["1.5rem", "2rem", "3rem"],
            padding_y="2rem",
        ),
        on_unmount=HomeState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
