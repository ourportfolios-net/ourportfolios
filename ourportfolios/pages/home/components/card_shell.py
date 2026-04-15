"""Shared styling primitives for Home page cards."""

from __future__ import annotations

import reflex as rx

from ....styles import CARD_BG, CARD_BORDER, SKELETON_BG, white
from ....ui.tokens import CARD_PREVIEW_HEIGHT, CARD_TEXT_CLAMP_STYLE

CARD_HEADER_HEIGHT = "4.25rem"
CARD_BODY_HEIGHT = "26.25rem"
CARD_PREVIEW_SURFACE_HEIGHT = CARD_PREVIEW_HEIGHT
HUB_CARD_STYLE = {
    "background": CARD_BG,
    "border": CARD_BORDER,
    "border_radius": "0.875rem",
    "padding": "1.5rem",
    "position": "relative",
    "overflow": "hidden",
    "width": "100%",
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.055),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

HUB_CARD_TEXT_CLAMP = CARD_TEXT_CLAMP_STYLE


def skeleton(width: str, height: str = "0.5625rem") -> rx.Component:
    return rx.box(
        width=width, height=height, border_radius="0.25rem", background=SKELETON_BG
    )
