"""Reusable category toggle card used across settings UIs."""

import reflex as rx

from ourportfolios.styles import white


def category_toggle_card(
    title: str,
    checked,
    on_change,
    body: rx.Component,
    on_click=None,
) -> rx.Component:
    card = rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(title, size="5", weight="bold", color=white(0.92)),
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
        border_radius="0.625rem",
        background=white(0.025),
        border=f"1px solid {white(0.07)}",
        style={
            "transition": "all 0.15s ease",
            "_hover": {"background": white(0.035), "border_color": white(0.12)},
        },
        width="100%",
    )

    if on_click is None:
        return card

    return rx.box(card, on_click=on_click, cursor="pointer", width="100%")
