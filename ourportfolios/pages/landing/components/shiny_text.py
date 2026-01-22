"""ShinyText animated gradient shine text."""

import reflex as rx
from typing import Literal


class ShinyText(rx.Component):
    """Animated shine text component."""

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
    """Create an animated text with gradient shine effect."""
    # Coerce color values to plain strings for the component
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
