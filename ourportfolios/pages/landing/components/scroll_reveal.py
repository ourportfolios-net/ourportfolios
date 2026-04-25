"""ScrollReveal blur-to-sharp animation."""

import reflex as rx


class ScrollRevealComponent(rx.Component):
    """Scroll reveal animation component."""

    library = "$/public/ScrollReveal"
    tag = "ScrollReveal"

    blur_amount: int = 10
    initial_opacity: float = 0.4
    initial_scale: float = 0.98
    duration: float = 0.4
    delay: float = 0
    threshold: float = 0.1
    trigger_once: bool = True


def scroll_reveal(  # noqa: PLR0913
    *children: rx.Component,
    blur_amount: int = 10,
    initial_opacity: float = 0.4,
    initial_scale: float = 0.98,
    duration: float = 0.4,
    delay: float = 0,
    threshold: float = 0.1,
    trigger_once: bool = True,
    **props: object,
) -> rx.Component:
    """Animate children from blurry to sharp on scroll into view."""
    return ScrollRevealComponent.create(
        *children,
        blur_amount=blur_amount,
        initial_opacity=initial_opacity,
        initial_scale=initial_scale,
        duration=duration,
        delay=delay,
        threshold=threshold,
        trigger_once=trigger_once,
        **props,
    )
