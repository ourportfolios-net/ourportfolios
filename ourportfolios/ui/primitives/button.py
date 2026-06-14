"""Button primitives for consistent interactive elements."""

from __future__ import annotations

from typing import cast

import reflex as rx

from ourportfolios.ui.theme.colors import TEXT_PURPLE, purple, white
from ourportfolios.ui.theme.components import accent_button
from ourportfolios.ui.theme.surfaces import (
    BUTTON_COMPARE,
    BUTTON_FILTER_ACTIVE,
    BUTTON_GHOST,
    BUTTON_GHOST_SM,
    BUTTON_GHOST_XS,
    BUTTON_PURPLE,
    BUTTON_PURPLE_SM,
    BUTTON_SECONDARY,
    BUTTON_SECONDARY_ACTIVE,
    CHIP_STYLE,
    PILL_TOGGLE,
    PILL_TOGGLE_ACTIVE,
)
from ourportfolios.ui.tokens import (
    FONT_BASE,
    FONT_SM,
    RADIUS_SM,
    TRANS_DEFAULT,
    WEIGHT_REGULAR,
)


def primary_button(
    label: str,
    *,
    size: str = "2",
    **props: object,
) -> rx.Component:
    """Primary purple button.

    Args:
        label: Button text.
        size: Reflex button size.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": size,
            "style": BUTTON_PURPLE,
            **props,
        }),
    )


def primary_button_sm(
    label: str,
    **props: object,
) -> rx.Component:
    """Small primary purple button.

    Args:
        label: Button text.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": "1",
            "style": BUTTON_PURPLE_SM,
            **props,
        }),
    )


def ghost_button(
    label: str,
    *,
    size: str = "2",
    **props: object,
) -> rx.Component:
    """Ghost button with subtle background.

    Args:
        label: Button text.
        size: Reflex button size.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": size,
            "style": BUTTON_GHOST,
            **props,
        }),
    )


def ghost_button_sm(
    label: str,
    **props: object,
) -> rx.Component:
    """Small ghost button.

    Args:
        label: Button text.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": "1",
            "style": BUTTON_GHOST_SM,
            **props,
        }),
    )


def ghost_button_xs(
    label: str,
    **props: object,
) -> rx.Component:
    """Extra-small ghost button.

    Args:
        label: Button text.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": "1",
            "style": BUTTON_GHOST_XS,
            **props,
        }),
    )


def secondary_button(
    label: str | rx.Component,
    *,
    active: object = False,
    **props: object,
) -> rx.Component:
    """Secondary button, optionally in active state.

    Args:
        label: Button text.
        active: Reflex Var[bool] or bool for active state.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "style": rx.cond(active, BUTTON_SECONDARY_ACTIVE, BUTTON_SECONDARY),
            **props,
        }),
    )


def filter_button(
    label: str | rx.Component,
    *,
    active: object = False,
    **props: object,
) -> rx.Component:
    """Filter button with active highlight state.

    Args:
        label: Button text.
        active: Reflex Var[bool] or bool for active state.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "style": rx.cond(active, BUTTON_FILTER_ACTIVE, BUTTON_SECONDARY),
            **props,
        }),
    )


def pill_button(
    label: str | rx.Var[str],
    *,
    active: object = False,
    **props: object,
) -> rx.Component:
    """Pill-shaped toggle button with conditional active styling.

    Args:
        label: Button text or Reflex Var.
        active: Reflex Var[bool] or bool for active state.
        **props: Additional Reflex component props.

    """
    return rx.box(
        rx.text(
            label,
            size="1",
            weight="medium",
            color=rx.cond(active, "white", white(0.35)),
        ),
        **cast("dict", {
            "style": rx.cond(active, PILL_TOGGLE_ACTIVE, PILL_TOGGLE),
            **props,
        }),
    )


def compare_button(
    label: str,
    **props: object,
) -> rx.Component:
    """Compare-action button with purple accent.

    Args:
        label: Button text.
        **props: Additional Reflex button props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": "1",
            "style": BUTTON_COMPARE,
            **props,
        }),
    )


def chip_button(
    label: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Chip-style compact button.

    Args:
        label: Chip text or Reflex Var.
        **props: Additional Reflex component props.

    """
    return rx.box(
        rx.text(label, size="2", weight="medium", color=white(0.6)),
        **cast("dict", {
            "style": CHIP_STYLE,
            **props,
        }),
    )


def icon_button(
    icon_name: str,
    *,
    size: int = 16,
    style: dict[str, str | dict[str, str]] | None = None,
    **props: object,
) -> rx.Component:
    """Icon-only button with ghost styling.

    Args:
        icon_name: Reflex icon tag name.
        size: Icon size in px.
        style: Optional override style dict. Defaults to ``BUTTON_GHOST`` with compact padding.
        **props: Additional Reflex button props.

    """
    base_style: dict[str, str | dict[str, str]] = (
        {**BUTTON_GHOST, "padding": "0.35rem"} if style is None else style
    )
    return rx.button(
        rx.icon(icon_name, size=size),
        **cast("dict", {
            "style": base_style,
            **props,
        }),
    )


def icon_button_xs(
    icon_name: str,
    *,
    size: int = 13,
    style: dict[str, str | dict[str, str]] | None = None,
    **props: object,
) -> rx.Component:
    """Extra-small icon-only button, for compact contexts like table rows.

    Args:
        icon_name: Reflex icon tag name.
        size: Icon size in px.
        style: Optional override style dict. Defaults to ``BUTTON_GHOST_XS``.
        **props: Additional Reflex button props.

    """
    base_style: dict[str, str | dict[str, str]] = BUTTON_GHOST_XS if style is None else style
    return rx.button(
        rx.icon(icon_name, size=size),
        **cast("dict", {
            "size": "1",
            "style": base_style,
            **props,
        }),
    )


def toggle_button(
    label: str | rx.Var[str],
    *,
    active: object = False,
    on_click: object | None = None,
    **props: object,
) -> rx.Component:
    """Toggle button that switches between active and inactive visual states.

    Uses ``BUTTON_SECONDARY_ACTIVE`` / ``BUTTON_SECONDARY`` from the theme.

    Args:
        label: Button text or Reflex Var.
        active: Reflex Var[bool] or bool for active state.
        on_click: Click handler.
        **props: Additional Reflex component props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "style": rx.cond(active, BUTTON_SECONDARY_ACTIVE, BUTTON_SECONDARY),
            "on_click": on_click,
            **props,
        }),
    )


def pill_toggle(
    label: str | rx.Var[str],
    *,
    active: object = False,
    on_click: object | None = None,
    **props: object,
) -> rx.Component:
    """Pill-shaped toggle button with conditional active styling.

    Uses ``PILL_TOGGLE_ACTIVE`` / ``PILL_TOGGLE`` from the theme.

    Args:
        label: Button text or Reflex Var.
        active: Reflex Var[bool] or bool for active state.
        on_click: Click handler.
        **props: Additional Reflex component props.

    """
    return rx.button(
        label,
        **cast("dict", {
            "size": "2",
            "style": rx.cond(active, PILL_TOGGLE_ACTIVE, PILL_TOGGLE),
            "on_click": on_click,
            **props,
        }),
    )


def nav_link(
    label: str,
    href: str,
    **props: object,
) -> rx.Component:
    """Navigation link with consistent styling.

    Args:
        label: Link text.
        href: Destination URL.
        **props: Additional Reflex link props.

    """
    return rx.link(
        label,
        href=href,
        **cast("dict", {
            "font_size": FONT_BASE,
            "font_weight": WEIGHT_REGULAR,
            "color": white(0.5),
            "text_decoration": "none",
            "_hover": {"color": "white"},
            "transition": TRANS_DEFAULT,
            **props,
        }),
    )


def locked_link(
    label: str,
    _href: str,
    on_click: object,
    **props: object,
) -> rx.Component:
    """Locked navigation link that redirects to login on click.

    Args:
        label: Link text.
        _href: Intended destination (captured by on_click handler).
        on_click: Event handler for click.
        **props: Additional Reflex component props.

    """
    return rx.hstack(
        rx.text(label, font_size=FONT_SM, color=white(0.2)),
        rx.icon("lock", size=10, color=white(0.15)),
        **cast("dict", {
            "spacing": "1",
            "align": "center",
            "on_click": on_click,
            "cursor": "pointer",
            "title": "Sign in to access",
            "_hover": {"opacity": "0.6"},
            "transition": TRANS_DEFAULT,
            **props,
        }),
    )


def accent_link(
    label: str,
    icon: str = "arrow-right",
    href: str | None = None,
    on_click: object | None = None,
    *,
    icon_left: bool = False,
    **props: object,
) -> rx.Component:
    """Accent link button with icon, used for "View More" type actions.

    Args:
        label: Link text.
        icon: Icon name.
        href: Optional destination URL.
        on_click: Optional click handler.
        icon_left: Whether icon appears before text.
        **props: Additional Reflex component props.

    """
    return accent_button(
        label,
        icon=icon,
        href=href,
        on_click=on_click,
        icon_left=icon_left,
        **cast("dict", props),
    )


def period_button(
    label: str,
    *,
    active: object = False,
    on_click: object | None = None,
    **props: object,
) -> rx.Component:
    """Period toggle button (1D, 1W, 1M, etc.) used in market overview.

    Args:
        label: Period label text.
        active: Reflex Var[bool] or bool for active state.
        on_click: Click handler.
        **props: Additional Reflex component props.

    """
    return rx.box(
        rx.text(
            label,
            size="1",
            weight="medium",
            color=rx.cond(active, TEXT_PURPLE, white(0.35)),
        ),
        **cast("dict", {
            "padding": "0.18rem 0.5rem",
            "border_radius": RADIUS_SM,
            "background": rx.cond(active, purple(0.18), "transparent"),
            "cursor": "pointer",
            "on_click": on_click,
            "_hover": {"background": rx.cond(active, purple(0.28), white(0.05))},
            "transition": TRANS_DEFAULT,
            **props,
        }),
    )
