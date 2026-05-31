"""Feedback primitives — skeletons, spinners, empty states."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.colors import purple, white
from ourportfolios.ui.tokens import RADIUS_SM, SPACE_SM, SPACE_XL


def skeleton_box(
    width: str = "100%",
    height: str = "0.75rem",
    radius: str = "0.375rem",
    **props: object,
) -> rx.Component:
    """Skeleton placeholder box.

    Args:
        width: Width of skeleton.
        height: Height of skeleton.
        radius: Border radius.
        **props: Additional Reflex skeleton props.

    """
    return rx.skeleton(
        rx.box(width=width, height=height),
        **{"loading": True, "border_radius": radius, **props},
    )


def skeleton_text(width: str = "100%", **props: object) -> rx.Component:
    """Skeleton placeholder for a line of text.

    Args:
        width: Width of text skeleton.
        **props: Additional Reflex skeleton props.

    """
    return skeleton_box(width=width, height="0.75rem", **props)


def skeleton_circle(
    size: str = "2rem",
    **props: object,
) -> rx.Component:
    """Skeleton placeholder for a circular element.

    Args:
        size: Size of the circle.
        **props: Additional Reflex skeleton props.

    """
    return rx.skeleton(
        rx.box(width=size, height=size),
        **{"loading": True, "border_radius": RADIUS_SM, **props},
    )


def loading_spinner(
    label: str | rx.Var[str] = "Loading...",
    **props: object,
) -> rx.Component:
    """Create a loading spinner with optional label.

    Args:
        label: Loading label text.
        **props: Additional Reflex spinner props.

    """
    return rx.center(
        rx.vstack(
            rx.spinner(
                thickness=3,
                size="2",
                speed="1s",
                color=purple(0.7),
            ),
            rx.text(label, size="2", color=white(0.5), margin_top=SPACE_SM),
            spacing="2",
            align="center",
        ),
        **{"width": "100%", "padding": SPACE_XL, **props},
    )


def empty_state(
    message: str,
    icon_size: int = 48,
    **props: object,
) -> rx.Component:
    """Empty state placeholder with icon and message.

    Args:
        message: Empty state message text.
        icon_size: Icon size in px.
        **props: Additional Reflex component props.

    """
    return rx.center(
        rx.vstack(
            rx.icon("inbox", size=icon_size, color=white(0.3)),
            rx.text(message, size="2", color=white(0.5)),
            spacing="2",
            align="center",
        ),
        **{"width": "100%", "padding": SPACE_XL, **props},
    )
