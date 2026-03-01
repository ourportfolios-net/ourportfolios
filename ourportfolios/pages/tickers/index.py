"""Tickers page — route definition only."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button

from .state import TickersPageState
from .page_layout import main_content


@rx.page(
    route="/tickers",
    on_load=TickersPageState.on_mount,
)
def index():
    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                main_content(),
                width="86vw",
                max_width="1800px",
            ),
            width="100%",
            padding="2em",
            padding_top="3em",
            padding_bottom="5em",
        ),
        drawer_button(),
        on_unmount=TickersPageState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
    )
