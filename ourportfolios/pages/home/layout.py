"""Home page shell and layout constants."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.ui.layout import app_shell, page_frame
from ourportfolios.ui.tokens import (
    HOME_CONTENT_MAX_WIDTH,
    HOME_CONTENT_WIDTH,
    HOME_PAGE_VERTICAL_PADDING,
)


def home_shell(content: rx.Component, on_unmount: object = None) -> rx.Component:
    return app_shell(
        navbar(),
        page_frame(
            content,
            width=HOME_CONTENT_WIDTH,
            max_width=HOME_CONTENT_MAX_WIDTH,
            padding_x="0",
            padding_y=HOME_PAGE_VERTICAL_PADDING,
        ),
        on_unmount=on_unmount,
    )
