"""Shared styling primitives for Home page cards."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import CARD_BG, CARD_BORDER, SKELETON_BG
from ourportfolios.ui.tokens import (
    CARD_PREVIEW_HEIGHT,
    CARD_TEXT_CLAMP_STYLE,
    RADIUS_5XS,
    RADIUS_CARD,
    TRANS_DEFAULT,
)

CARD_HEADER_HEIGHT = "4.25rem"
CARD_BODY_HEIGHT = "26.25rem"
CARD_PREVIEW_SURFACE_HEIGHT = CARD_PREVIEW_HEIGHT
HUB_CARD_STYLE = {
    "background": CARD_BG,
    "border": CARD_BORDER,
    "border_radius": RADIUS_CARD,
    "padding": rx.breakpoints(initial="1.125rem 1rem", md="1.5rem"),
    "position": "relative",
    "overflow": "hidden",
    "width": "100%",
    "transition": TRANS_DEFAULT,
    "_hover": {
        "background": white(0.055),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

HUB_CARD_TEXT_CLAMP = CARD_TEXT_CLAMP_STYLE


def skeleton(width: str, height: str = "0.5625rem") -> rx.Component:
    return rx.box(
        width=width, height=height, border_radius=RADIUS_5XS, background=SKELETON_BG,
    )
