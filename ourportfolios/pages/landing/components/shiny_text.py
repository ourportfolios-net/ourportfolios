"""ShinyText component for Reflex.

An animated text component with a moving gradient shine effect.
Based on reactbits.dev implementation using Framer Motion.
"""

import reflex as rx
from typing import Literal
import os


class ShinyText(rx.Component):
    """An animated text component with a moving gradient shine effect.

    This component creates text with an animated shine effect using Framer Motion.
    It requires the 'motion' npm package (Framer Motion).

    The component is based on the shiny text implementation from reactbits.dev.
    """

    # Reference the JSX file from the assets directory
    library = "$/public/ShinyText"

    tag = "ShinyText"
    is_default = True

    # Specify the npm dependency
    lib_dependencies: list[str] = ["motion@11.15.0"]

    # Component props
    text: rx.Var[str]
    disabled: rx.Var[bool] = False
    speed: rx.Var[float] = 2.0
    color: rx.Var[str] = "#b5b5b5"
    shine_color: rx.Var[str] = "#ffffff"
    spread: rx.Var[int] = 120
    yoyo: rx.Var[bool] = False
    pause_on_hover: rx.Var[bool] = False
    direction: rx.Var[Literal["left", "right"]] = "left"
    delay: rx.Var[float] = 0.0


def shiny_text(
    text: str,
    disabled: bool = False,
    speed: float = 2.0,
    color: str = "#b5b5b5",
    shine_color: str = "#ffffff",
    spread: int = 120,
    yoyo: bool = False,
    pause_on_hover: bool = False,
    direction: Literal["left", "right"] = "left",
    delay: float = 0.0,
    **props,
) -> rx.Component:
    """Create an animated text with moving gradient shine effect.

    Args:
        text: The text content to display with shine effect (required)
        disabled: Disable the animation (default: False)
        speed: Animation speed in seconds (default: 2.0)
        color: Base text color (default: "#b5b5b5")
        shine_color: Color of the shine highlight (default: "#ffffff")
        spread: Gradient spread angle in degrees (default: 120)
        yoyo: Enable back-and-forth animation (default: False)
        pause_on_hover: Pause animation on mouse hover (default: False)
        direction: Animation direction - "left" or "right" (default: "left")
        delay: Delay before animation loop in seconds (default: 0.0)
        **props: Additional props including style props (font_size, font_weight, etc.)

    Returns:
        The ShinyText component configured with the specified parameters.

    Example:
        ```python
        # Basic usage
        shiny_text("Hello World")

        # Customized
        shiny_text(
            "OurPortfolios",
            speed=3,
            color="#ffffff",
            shine_color="#60a5fa",
            spread=100,
            direction="right",
        )
        ```
    """
    # Ensure colors are strings: Reflex `rx.color(...)` returns a Color
    # object which stringifies to a CSS variable (e.g. "var(--gray-12)").
    # The ShinyText prop expects a plain string, so coerce non-strings.
    if not isinstance(color, str):
        color = str(color)
    if not isinstance(shine_color, str):
        shine_color = str(shine_color)

    return ShinyText.create(
        text=text,
        disabled=disabled,
        speed=speed,
        color=color,
        shine_color=shine_color,
        spread=spread,
        yoyo=yoyo,
        pause_on_hover=pause_on_hover,
        direction=direction,
        delay=delay,
        **props,
    )
