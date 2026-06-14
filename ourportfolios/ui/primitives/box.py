"""Low-level box/surface primitives for consistent container styling."""

from __future__ import annotations

from typing import cast

import reflex as rx

from ourportfolios.ui.theme.colors import purple, white
from ourportfolios.ui.theme.components import glow_orb_style, icon_box_style, icon_color
from ourportfolios.ui.theme.surfaces import (
    CARD_BG,
    CARD_BORDER,
    CARD_HOVER_STYLE,
    MODAL_BG,
    SUBTLE_BG,
    SUBTLE_BORDER,
    SURFACE_BG,
    SURFACE_BORDER,
)
from ourportfolios.ui.tokens import (
    BLUR_DEFAULT,
    RADIUS_CARD,
    RADIUS_INPUT,
    RADIUS_SM,
    RADIUS_SURFACE,
    SHADOW_LG,
    TRANS_DEFAULT,
    TRANS_FAST,
)


def surface_box(
    *children: rx.Component,
    padding: str = "1.5rem",
    hover: bool = False,
    **props: object,
) -> rx.Component:
    """Create a standard card/surface box with consistent background, border, and radius."""
    style: dict[str, object] = {
        "background": CARD_BG,
        "border": CARD_BORDER,
        "border_radius": RADIUS_CARD,
        "padding": padding,
    }
    if hover:
        style.update(CARD_HOVER_STYLE)
    if "style" in props:
        style.update(cast("dict[str, object]", props.pop("style")))
    rest = {
        "style": style,
        **props,
    }
    return rx.box(*children, **cast("dict", rest))


def glass_box(
    *children: rx.Component,
    padding: str | int = "1rem",
    width: str | int | None = None,
    **props: object,
) -> rx.Component:
    """Glass-morphism card with backdrop blur."""
    return rx.box(
        *children,
        **cast("dict", {
            "padding": padding,
            "border_radius": RADIUS_CARD,
            "background": white(0.03),
            "backdrop_filter": f"blur({BLUR_DEFAULT})",
            "border": CARD_BORDER,
            "width": width,
            "transition": TRANS_DEFAULT,
            "_hover": {
                "background": white(0.055),
                "border_color": white(0.13),
            },
            **props,
        }),
    )


def subtle_box(
    *children: rx.Component,
    padding: str = "0.75rem",
    **props: object,
) -> rx.Component:
    """Subtle surface for nested/secondary content."""
    return rx.box(
        *children,
        **cast("dict", {
            "padding": padding,
            "border_radius": RADIUS_INPUT,
            "background": SUBTLE_BG,
            "border": SUBTLE_BORDER,
            **props,
        }),
    )


def section_container(
    *children: rx.Component,
    padding: str = "1.25rem 1.5rem",
    **props: object,
) -> rx.Component:
    """Section-level container with standard section padding."""
    return rx.box(
        *children,
        **cast("dict", {
            "padding": padding,
            "border_radius": RADIUS_CARD,
            "background": SURFACE_BG,
            "border": SURFACE_BORDER,
            **props,
        }),
    )


def modal_panel(
    *children: rx.Component,
    width: str = "60vw",
    height: str = "58vh",
    padding: str = "2rem",
    max_width: str | None = None,
    **props: object,
) -> rx.Component:
    """Modal dialog panel with consistent styling."""
    extra: dict[str, object] = {}
    if max_width:
        extra["max_width"] = max_width
    return rx.box(
        *children,
        **cast("dict", {
            "width": width,
            "height": height,
            "padding": padding,
            "background": MODAL_BG,
            "border": f"1px solid {white(0.08)}",
            "border_radius": RADIUS_CARD,
            "box_shadow": SHADOW_LG,
            **extra,
            **props,
        }),
    )


def overlay_box(
    is_active: object,
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Overlay container that shows/hides based on a condition."""
    return rx.box(
        *children,
        **cast("dict", {
            "position": "absolute",
            "inset": "0",
            "opacity": rx.cond(is_active, "1", "0"),
            "pointer_events": rx.cond(is_active, "auto", "none"),
            "transition": TRANS_FAST,
            **props,
        }),
    )


def icon_container(
    icon_name: str,
    color: str = "purple",
    size: int = 16,
    container_size: str = "2.5rem",
    **props: object,
) -> rx.Component:
    """Icon inside a styled container box."""
    return rx.box(
        rx.icon(icon_name, size=size, color=icon_color(color)),
        style=icon_box_style(color=color, size=container_size),
        **cast("dict", props),
    )


def metric_box(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Small metric display box used in landing page cards."""
    return rx.box(
        *children,
        **cast("dict", {
            "flex": "1",
            "padding": "0.875rem",
            "background": white(0.02),
            "border": f"1px solid {white(0.07)}",
            "border_radius": RADIUS_INPUT,
            **props,
        }),
    )


def chart_box(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Chart container box used in landing page cards."""
    return rx.box(
        *children,
        **cast("dict", {
            "flex": "1",
            "padding": "0.75rem",
            "background": white(0.02),
            "border": f"1px solid {white(0.07)}",
            "border_radius": RADIUS_SURFACE,
            **props,
        }),
    )


def list_row(
    *children: rx.Component,
    selected: object = False,
    **props: object,
) -> rx.Component:
    """List row item used in landing page ticker lists."""
    return rx.box(
        *children,
        **cast("dict", {
            "width": "100%",
            "padding": "1rem 1.25rem",
            "background": rx.cond(selected, purple(0.1), white(0.02)),
            "border": rx.cond(
                selected,
                f"1px solid {purple(0.25)}",
                f"1px solid {white(0.07)}",
            ),
            "border_radius": RADIUS_SURFACE,
            **props,
        }),
    )


def navbar_bar(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Create a fixed navigation bar with blur backdrop."""
    return rx.box(
        *children,
        **cast("dict", {
            "position": "fixed",
            "top": "0",
            "width": "100%",
            "z_index": "50",
            "padding_y": "1rem",
            "background": "rgba(10, 10, 10, 0.4)",
            "backdrop_filter": f"blur({BLUR_DEFAULT})",
            "border_bottom": f"1px solid {white(0.09)}",
            "box_shadow": SHADOW_LG,
            **props,
        }),
    )


def dropdown_panel(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Dropdown/hover-card panel with dark surface styling."""
    return rx.box(
        *children,
        **cast("dict", {
            "background": "rgba(13, 13, 15, 0.97)",
            "border": f"1px solid {white(0.07)}",
            "border_radius": RADIUS_SURFACE,
            "padding": "0.375rem",
            "box_shadow": SHADOW_LG,
            **props,
        }),
    )


def user_avatar(
    initial: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """User avatar square with initial letter."""
    return rx.box(
        rx.text(
            initial,
            font_size="0.75rem",
            font_weight="600",
            color=white(0.8),
            line_height="1",
            user_select="none",
        ),
        **cast("dict", {
            "width": "2rem",
            "height": "2rem",
            "border_radius": RADIUS_SM,
            "background": white(0.06),
            "border": f"1px solid {white(0.11)}",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "cursor": "pointer",
            "flex_shrink": "0",
            "transition": TRANS_DEFAULT,
            "_hover": {"background": white(0.1), "border_color": white(0.2)},
            **props,
        }),
    )


def glow_orb(
    color: str = "purple",
    **props: object,
) -> rx.Component:
    """Create a decorative glow orb for card backgrounds."""
    return rx.box(
        style=glow_orb_style(color=color),
        **cast("dict", props),
    )
