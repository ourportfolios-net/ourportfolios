import reflex as rx
from ...state.home_state import HomeState
from ...components.navbar import navbar
from .page_body import page_body


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            page_body(),
            width="90vw",
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
