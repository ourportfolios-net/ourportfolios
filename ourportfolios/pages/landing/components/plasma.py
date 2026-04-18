"""Plasma background component."""

from typing import Literal

import reflex as rx


class Plasma(rx.Component):
    """WebGL plasma effect component."""

    # Reference the JSX file from the assets directory
    library = "$/public/Plasma"

    tag = "Plasma"
    is_default = True

    # Specify the npm dependency
    lib_dependencies: list[str] = ["ogl@1.0.6"]

    # Component props
    color: rx.Var[str] = "#ffffff"
    speed: rx.Var[float] = 1.0
    direction: rx.Var[Literal["forward", "reverse", "pingpong"]] = "forward"
    scale: rx.Var[float] = 1.0
    opacity: rx.Var[float] = 1.0
    mouse_interactive: rx.Var[bool] = True


def plasma(
    color: str = "#ffffff",
    speed: float = 1.0,
    direction: Literal["forward", "reverse", "pingpong"] = "forward",
    scale: float = 1.0,
    opacity: float = 1.0,
    mouse_interactive: bool = True,
    **props,
) -> rx.Component:
    """Create a Plasma background effect component."""
    return Plasma.create(
        color=color,
        speed=speed,
        direction=direction,
        scale=scale,
        opacity=opacity,
        mouse_interactive=mouse_interactive,
        **props,
    )
