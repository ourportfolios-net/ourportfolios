"""Plasma background component for Reflex.

A WebGL-powered plasma effect background component based on reactbits.dev implementation.
"""

import reflex as rx
from typing import Literal
import os


class Plasma(rx.Component):
    """A WebGL plasma effect background component.

    This component creates an animated plasma effect using WebGL 2.
    It requires the 'ogl' npm package to be installed.

    The component is based on the plasma implementation from reactbits.dev.
    """

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
    """Create a Plasma background effect component.

    Args:
        color: Hex color string for the plasma effect (default: "#ffffff")
        speed: Animation speed multiplier, 0.1-3.0 recommended (default: 1.0)
        direction: Animation direction - "forward", "reverse", or "pingpong" (default: "forward")
        scale: Zoom scale, higher values = more zoomed out, 0.5-3.0 recommended (default: 1.0)
        opacity: Opacity of the effect, 0.0-1.0 (default: 1.0)
        mouse_interactive: Enable mouse interaction for dynamic warping (default: True)
        **props: Additional props including style props (position, z_index, width, height, etc.)

    Returns:
        The Plasma component configured with the specified parameters.

    Example:
        ```python
        # As a fixed background
        plasma(
            color="#3b82f6",
            speed=0.6,
            scale=2,
            opacity=0.2,
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="-1",
        )
        ```
    """
    return Plasma.create(
        color=color,
        speed=speed,
        direction=direction,
        scale=scale,
        opacity=opacity,
        mouse_interactive=mouse_interactive,
        **props,
    )
