from typing import Any, cast

import reflex as rx

from ourportfolios.pages.home.layout import home_shell
from ourportfolios.pages.home.sections.dashboard import page_body
from ourportfolios.state.home_state import HomeState


@rx.page(route="/home", on_load=cast("Any", HomeState.on_mount))
def index() -> rx.Component:
    return home_shell(
        page_body(),
        on_unmount=cast("Any", HomeState.on_unmount),
    )
