from typing import Any, cast

import reflex as rx

from ...state.home_state import HomeState
from .layout import home_shell
from .page_body import page_body


@rx.page(route="/home", on_load=cast(Any, HomeState.on_mount))
def index() -> rx.Component:
    return home_shell(
        page_body(),
        on_unmount=cast(Any, HomeState.on_unmount),
    )
