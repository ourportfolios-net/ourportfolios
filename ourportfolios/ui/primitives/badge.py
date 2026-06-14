"""Custom badge component with consistent design tokens."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.tokens import RADIUS_SM

_BADGE_STYLE: dict[str, str] = {
    "border_radius": RADIUS_SM,
    "padding": "0.18rem 0.5rem",
    "font_size": "0.6875rem",
    "font_weight": "500",
    "white_space": "nowrap",
    "display": "inline-flex",
    "align_items": "center",
    "justify_content": "center",
    "line_height": "1.2",
}

_VARIANTS: dict[str, dict[str, object]] = {
    "gray": {
        "background": white(0.06),
        "border": f"1px solid {white(0.1)}",
        "color": white(0.65),
    },
    "green": {
        "background": "rgba(52,211,153,0.1)",
        "border": "1px solid rgba(52,211,153,0.25)",
        "color": "rgba(52,211,153,0.9)",
    },
    "red": {
        "background": "rgba(239,68,68,0.1)",
        "border": "1px solid rgba(239,68,68,0.25)",
        "color": "rgba(239,68,68,0.9)",
    },
    "blue": {
        "background": rx.color("blue", 2),
        "border": f"1px solid {rx.color('blue', 6)}",
        "color": rx.color("blue", 11),
    },
    "indigo": {
        "background": rx.color("indigo", 2),
        "border": f"1px solid {rx.color('indigo', 6)}",
        "color": rx.color("indigo", 11),
    },
    "sky": {
        "background": rx.color("sky", 2),
        "border": f"1px solid {rx.color("sky", 6)}",
        "color": rx.color("sky", 11),
    },
    "cyan": {
        "background": rx.color("cyan", 2),
        "border": f"1px solid {rx.color("cyan", 6)}",
        "color": rx.color("cyan", 11),
    },
    "teal": {
        "background": rx.color("teal", 2),
        "border": f"1px solid {rx.color("teal", 6)}",
        "color": rx.color("teal", 11),
    },
    "amber": {
        "background": rx.color("amber", 2),
        "border": f"1px solid {rx.color("amber", 6)}",
        "color": rx.color("amber", 11),
    },
    "orange": {
        "background": rx.color("orange", 2),
        "border": f"1px solid {rx.color("orange", 6)}",
        "color": rx.color("orange", 11),
    },
    "pink": {
        "background": rx.color("pink", 2),
        "border": f"1px solid {rx.color("pink", 6)}",
        "color": rx.color("pink", 11),
    },
    "plum": {
        "background": rx.color("plum", 2),
        "border": f"1px solid {rx.color("plum", 6)}",
        "color": rx.color("plum", 11),
    },
    "purple": {
        "background": rx.color("violet", 2),
        "border": f"1px solid {rx.color("violet", 6)}",
        "color": rx.color("violet", 11),
    },
    "violet": {
        "background": rx.color("violet", 2),
        "border": f"1px solid {rx.color("violet", 6)}",
        "color": rx.color("violet", 11),
    },
    "accent": {
        "background": rx.color("violet", 2),
        "border": f"1px solid {rx.color("violet", 6)}",
        "color": rx.color("violet", 11),
    },
}


def badge(
    *children: object,
    color_variant: str | rx.Var[str] = "gray",
    **kwargs: str | float | bool | list | dict,
) -> rx.Component:
    """Render a custom badge with consistent design tokens.

    Args:
        *children: Child components or text content.
        color_variant: One of "gray", "green", "red", "blue", "indigo",
            "sky", "cyan", "teal", "amber", "orange", "pink", "plum",
            "purple", "violet", "accent".
        **kwargs: Additional style overrides passed to rx.box.

    Returns:
        A styled badge component.

    """
    variant_style = _VARIANTS.get(color_variant, _VARIANTS["gray"])
    return rx.box(
        *children,
        style={**_BADGE_STYLE, **variant_style, **kwargs},
    )
