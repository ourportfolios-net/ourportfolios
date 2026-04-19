"""Layout helpers shared across app pages."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.tokens import (
    APP_BG,
    PAGE_EDGE_PADDING,
    PAGE_MAX_WIDTH,
    PAGE_VERTICAL_PADDING,
)


def clamp_lines(lines: int) -> dict[str, str]:
    return {
        "display": "-webkit-box",
        "-webkit-line-clamp": str(lines),
        "-webkit-box-orient": "vertical",
        "overflow": "hidden",
    }


def page_frame(
    *children: rx.Component,
    max_width: str = PAGE_MAX_WIDTH,
    width: str = "100%",
    padding_x: str = PAGE_EDGE_PADDING,
    padding_y: str = PAGE_VERTICAL_PADDING,
) -> rx.Component:
    return rx.box(
        *children,
        width=width,
        max_width=max_width,
        margin="0 auto",
        padding_x=padding_x,
        padding_y=padding_y,
    )


def app_shell(*children: rx.Component, **props: object) -> rx.Component:
    return rx.box(
        *children,
        background=APP_BG,
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
        **props,
    )
