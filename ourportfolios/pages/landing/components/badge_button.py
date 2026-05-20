"""Badge button component."""

from typing import Literal

import reflex as rx

from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import CARD_STYLE
from ourportfolios.ui.tokens import (
    BLUR_XL,
    FONT_LABEL,
    LETTER_NORMAL,
    RADIUS_BUTTON,
    TRANS_SLOW,
)

_BADGE_BUTTON_STYLE = {
    "background": CARD_STYLE["background"],
    "border": CARD_STYLE["border"],
    "border_radius": RADIUS_BUTTON,
    "backdrop_filter": f"blur({BLUR_XL})",
    "cursor": "pointer",
    "transition": TRANS_SLOW,
    "_hover": {
        "background": white(0.08),
        "border": f"1px solid {white(0.1)}",
    },
}


def badge_button(
    text: str,
    *,
    size: Literal["1", "2", "3", "4"] = "2",
    padding_x: str = "1rem",
    padding_y: str = "0.375rem",
) -> rx.Component:
    """Create a badge-style button with pulsing dot."""
    return rx.button(
        rx.hstack(
            rx.box(
                width="0.25rem",
                height="0.25rem",
                border_radius="9999px",
                background="#7C3AED",
                animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            ),
            rx.text(
                text,
                font_size=FONT_LABEL,
                letter_spacing=LETTER_NORMAL,
                text_transform="uppercase",
            ),
            spacing="2",
            align="center",
        ),
        size=size,
        padding_x=padding_x,
        padding_y=padding_y,
        style=_BADGE_BUTTON_STYLE,
    )
