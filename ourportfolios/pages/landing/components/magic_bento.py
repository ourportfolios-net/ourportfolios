"""MagicBento component for Reflex.

A beautiful bento-style grid layout with interactive spotlight effects.
Inspired by reactbits.dev magic-bento component.
"""

import reflex as rx
from typing import Any


class MagicBentoCard(rx.Component):
    """Interactive bento card with spotlight and tilt effects.

    Features:
    - Mouse-following spotlight with purple glow
    - 3D tilt effect on hover
    - Animated border glow
    - Magnetic scale effect
    - Glass morphism design
    """

    library = "$/public/MagicBento"
    tag = "MagicBentoCard"

    lib_dependencies: list[str] = ["motion@11.15.0"]

    # Component props
    spotlight_radius: rx.Var[int] = 60
    enable_tilt: rx.Var[bool] = True
    enable_magnetism: rx.Var[bool] = True


class MagicBento(rx.Component):
    """Container for MagicBento grid layout.

    Creates a responsive CSS grid that holds MagicBentoCard components.
    """

    library = "$/public/MagicBento"
    tag = "MagicBento"

    lib_dependencies: list[str] = ["motion@11.15.0"]

    # Component props
    columns: rx.Var[int] = 3
    gap: rx.Var[str] = "1rem"


def magic_bento_card(
    *children,
    spotlight_radius: int = 60,
    enable_tilt: bool = True,
    enable_magnetism: bool = True,
    **props,
) -> rx.Component:
    """Create an interactive magic bento card.

    The card features:
    - A spotlight effect that follows the mouse cursor
    - 3D tilt effect based on mouse position
    - Animated glowing border on hover
    - Scale animation on hover (if magnetism enabled)
    - Glass morphism styling with blur effects

    Args:
        *children: Child components to display in the card
        spotlight_radius: Radius of spotlight effect in pixels (default: 60)
        enable_tilt: Enable 3D tilt on hover (default: True)
        enable_magnetism: Enable magnetic scale effect (default: True)
        **props: Additional props including:
            - padding: Card padding (e.g., "2rem", "2.5rem")
            - min_height: Minimum card height (e.g., "18.75rem", "25rem")
            - grid_column: CSS grid column span (e.g., ["1 / -1", "1 / 3"])
            - Other standard Reflex/CSS props

    Returns:
        The MagicBentoCard component configured with the specified parameters.

    Example:
        ```python
        magic_bento_card(
            rx.vstack(
                rx.heading("Feature Title"),
                rx.text("Feature description"),
            ),
            spotlight_radius=80,
            padding="2rem",
            min_height="20rem",
            grid_column=["1 / -1", "1 / 3"],  # Responsive spans
        )
        ```
    """
    return MagicBentoCard.create(
        *children,
        spotlight_radius=spotlight_radius,
        enable_tilt=enable_tilt,
        enable_magnetism=enable_magnetism,
        **props,
    )


def magic_bento(
    *children,
    columns: int = 3,
    gap: str = "1rem",
    **props,
) -> rx.Component:
    """Create a magic bento grid container.

    This component creates a CSS Grid layout that automatically arranges
    MagicBentoCard components. Cards can span multiple columns using the
    grid_column prop.

    Args:
        *children: MagicBentoCard components to display in the grid
        columns: Number of columns in the grid (default: 3)
        gap: Gap between grid items (default: "1rem")
        **props: Additional props including:
            - width: Grid width (default: "100%")
            - max_width: Maximum grid width (e.g., "80rem")
            - Other standard Reflex/CSS props

    Returns:
        The MagicBento container configured with the specified parameters.

    Example:
        ```python
        magic_bento(
            magic_bento_card(...),
            magic_bento_card(...),
            magic_bento_card(...),
            columns=3,
            gap="1.5rem",
            max_width="80rem",
        )
        ```

    Note:
        For responsive layouts, use CSS Grid directly on the parent box
        and set grid_column on individual cards:

        ```python
        rx.box(
            magic_bento_card(..., grid_column=["1 / -1", "1 / 3"]),
            magic_bento_card(..., grid_column=["1 / -1", "3 / 5"]),
            display="grid",
            grid_template_columns=["1fr", "1fr", "repeat(6, 1fr)"],
            gap="1.5rem",
        )
        ```
    """
    return MagicBento.create(
        *children,
        columns=columns,
        gap=gap,
        **props,
    )
