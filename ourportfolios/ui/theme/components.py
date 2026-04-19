"""Reusable UI component helpers and extended style presets."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.colors import blue, green, indigo, purple, white
from ourportfolios.ui.theme.surfaces import CARD_HOVER_STYLE


def accent_btn(
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
        border_radius="0.5rem",
        transition="all 0.15s ease",
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


def ghost_btn(
    label: str,
    icon: str = "arrow-right",
    href: str | None = None,
    on_click: object | None = None,
) -> rx.Component:
    return accent_btn(label, icon=icon, href=href, on_click=on_click)


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
        border_radius="0.625rem",
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
        "filter": "blur(3rem)",
        "border_radius": "9999px",
        "pointer_events": "none",
    }


def skeleton_box_style(
    width: str,
    height: str,
    radius: str = "0.25rem",
    opacity: float = 0.06,
) -> dict:
    return {
        "width": width,
        "height": height,
        "border_radius": radius,
        "background": f"rgba(255, 255, 255, {opacity})",
        "flex_shrink": "0",
    }


def overlay_style(is_active: object) -> dict:
    return {
        "opacity": rx.cond(is_active, "1", "0"),
        "pointer_events": rx.cond(is_active, "auto", "none"),
        "transition": "opacity 0.15s ease",
        "position": "absolute",
        "inset": "0",
    }


LANDING_CARD = {
    "background": "transparent",
    "backdrop_filter": "blur(1.25rem)",
    "border": f"1px solid {white(0.07)}",
    "border_radius": "1.5rem",
    "display": "flex",
    "flex_direction": "column",
}

LANDING_METRIC_BOX = {
    "flex": "1",
    "padding": "0.875rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.625rem",
}

LANDING_CHART_BOX = {
    "flex": "1",
    "padding": "0.75rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW_SELECTED = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": purple(0.1),
    "border": f"1px solid {purple(0.25)}",
    "border_radius": "0.75rem",
}


TABLE_CELL_BORDER = f"1px solid {white(0.04)}"

TICKER_CARD_STYLE = {
    "transition": "all 0.2s ease",
    "marginLeft": "0.6em",
    "_hover": {"marginLeft": "0"},
}

CARD_HOVER = CARD_HOVER_STYLE
DECISION_HUB_HOVER = {}
