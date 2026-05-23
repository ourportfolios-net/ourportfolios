"""Reusable UI component helpers and extended style presets."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.colors import blue, green, indigo, purple, white
from ourportfolios.ui.tokens import (
    BLUR_DEFAULT,
    RADIUS_INPUT,
    RADIUS_SM,
    TRANS_DEFAULT,
    TRANS_FAST,
)


def accent_button(
    label: str,
    icon: str = "arrow-right",
    href: str | None = None,
    on_click: object | None = None,
    *,
    icon_left: bool = False,
) -> rx.Component:
    icon_el = rx.icon(icon, size=12, color=white(0.5))
    label_el = rx.text(label, size="1", weight="medium", color=white(0.65))
    children = [icon_el, label_el] if icon_left else [label_el, icon_el]

    inner = rx.box(
        rx.hstack(*children, spacing="1", align="center"),
        padding="0.35em 0.75em",
        background=white(0.04),
        border=f"1px solid {white(0.09)}",
        border_radius=RADIUS_SM,
        transition=TRANS_DEFAULT,
        _hover={"background": white(0.09), "border_color": white(0.2)},
        cursor="pointer",
        align_self="flex-end",
        position="relative",
        z_index="2",
        display="inline-flex",
    )
    if href:
        return rx.link(
            inner,
            href=href,
            underline="none",
            align_self="flex-end",
            position="relative",
            z_index="2",
        )
    if on_click:
        return rx.box(
            inner,
            on_click=on_click,
            cursor="pointer",
            align_self="flex-end",
            position="relative",
            z_index="2",
        )
    return inner


_ICON_COLORS = {
    "purple": (purple(0.12), purple(0.25), "rgba(167, 139, 250, 0.9)"),
    "blue": (blue(0.12), blue(0.25), "rgba(96, 165, 250, 0.9)"),
    "green": (green(0.12), green(0.25), "rgba(52, 211, 153, 0.9)"),
    "indigo": (indigo(0.1), indigo(0.2), "rgba(129, 140, 248, 0.85)"),
}


def icon_box(icon_name: str, color: str = "purple", size: int = 16) -> rx.Component:
    bg, border, icon_color_val = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return rx.box(
        rx.icon(icon_name, size=size, color=icon_color_val),
        background=bg,
        border=f"1px solid {border}",
        border_radius=RADIUS_INPUT,
        padding="0.5625rem",
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def icon_box_style(
    color: str = "purple",
    size: str = "2.5rem",
    radius: str = "0.625rem",
) -> dict:
    bg, border, _ = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return {
        "width": size,
        "height": size,
        "border_radius": radius,
        "background": bg,
        "border": f"1px solid {border}",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "flex_shrink": "0",
    }


def icon_color(color: str = "purple") -> str:
    _, _, c = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return c


def glow_orb_style(color: str = "purple") -> dict:
    colors = {"purple": purple(0.07), "blue": blue(0.07), "green": green(0.07)}
    return {
        "position": "absolute",
        "right": "-2rem",
        "top": "-2rem",
        "width": "8rem",
        "height": "8rem",
        "background": colors.get(color, colors["purple"]),
        "filter": f"blur({BLUR_DEFAULT})",
        "border_radius": RADIUS_SM,
        "pointer_events": "none",
    }


def overlay_style(is_active: object) -> dict:
    return {
        "opacity": rx.cond(is_active, "1", "0"),
        "pointer_events": rx.cond(is_active, "auto", "none"),
        "transition": TRANS_FAST,
        "position": "absolute",
        "inset": "0",
    }
