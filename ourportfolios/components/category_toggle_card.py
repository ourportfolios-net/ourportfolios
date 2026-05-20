"""Reusable category toggle card used across settings UIs."""

from collections.abc import Callable

import reflex as rx

from ourportfolios.ui.primitives import body_text
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.tokens import (
    RADIUS_SM,
    TRANS_DEFAULT,
)


def category_toggle_card(
    title: str,
    *,
    checked: bool | rx.Var[bool],
    on_change: Callable[..., object],
    body: rx.Component,
    on_click: Callable[..., object] | None = None,
) -> rx.Component:
    card = rx.box(
        rx.vstack(
            rx.hstack(
                body_text(title, weight="bold", color=white(0.92)),
                rx.spacer(),
                rx.checkbox(
                    checked=checked,
                    on_change=on_change,
                    size="2",
                    color_scheme="violet",
                ),
                width="100%",
                align="center",
            ),
            body,
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="0.75em 0.9em",
        border_radius=RADIUS_SM,
        background=white(0.025),
        border=f"1px solid {white(0.07)}",
        _hover={"background": white(0.035), "border_color": white(0.12)},
        transition=TRANS_DEFAULT,
        width="100%",
    )

    if on_click is None:
        return card

    return rx.box(card, on_click=on_click, cursor="pointer", width="100%")
