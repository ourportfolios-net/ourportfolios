import reflex as rx

from ourportfolios.pages.home.layout import home_shell
from ourportfolios.pages.home.sections.dashboard import page_body
from ourportfolios.state.home_state import HomeState


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    return rx.box(
        home_shell(page_body()),
        on_unmount=HomeState.on_unmount,
    )
