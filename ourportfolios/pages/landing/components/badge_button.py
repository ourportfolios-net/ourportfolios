"""Badge button component."""

import reflex as rx


def badge_button(text: str, **props: object) -> rx.Component:
    """Create a badge-style button with pulsing dot."""
    padding_x = props.pop("padding_x", "1rem")
    padding_y = props.pop("padding_y", "0.375rem")

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
                font_size="0.625rem",
                letter_spacing="0.2em",
                text_transform="uppercase",
            ),
            spacing="2",
            align="center",
        ),
        padding_x=padding_x,
        padding_y=padding_y,
        border_radius="0.75rem",
        background="rgba(255, 255, 255, 0.03)",
        backdrop_filter="blur(1.5rem)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        _hover={
            "background": "rgba(255, 255, 255, 0.08)",
            "border": "1px solid rgba(255, 255, 255, 0.1)",
        },
        transition="all 0.2s",
        cursor="pointer",
        **props,
    )
