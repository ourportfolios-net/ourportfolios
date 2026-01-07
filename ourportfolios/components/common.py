"""Common reusable UI components used across pages."""

import reflex as rx


def page_navigation_card(
    icon_left: bool = False,
    icon_right: bool = False,
    title: str = "",
    subtitle: str = "",
    href: str = "/",
    size: str = "7",
) -> rx.Component:
    """Create a navigation card with optional left/right chevron icons."""
    content = rx.vstack(
        rx.heading(title, weight="regular" if size == "7" else "medium", size=size),
        rx.text(subtitle, size="3" if size == "7" else "1"),
        align="center",
        justify="center",
        height="100%",
        spacing="1",
    )

    if icon_left:
        return rx.hstack(
            rx.icon("chevron_left", size=32),
            content,
            align="center",
            justify="center",
        )
    elif icon_right:
        return rx.hstack(
            content,
            rx.icon("chevron_right", size=32),
            align="center",
            justify="center",
        )
    else:
        return content


def card_wrapper(*content, style=None) -> rx.Component:
    """Wrap content in a transparent card container."""
    style = style or {}
    return rx.card(
        *content,
        border="none",
        background_color="transparent",
        style=style,
        spacing="4",
    )


def loading_spinner(size: str = "3") -> rx.Component:
    """Create a centered loading spinner."""
    return rx.center(rx.spinner(size=size))
