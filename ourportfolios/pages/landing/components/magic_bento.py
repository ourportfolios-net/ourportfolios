"""MagicBento Reflex component."""

from typing import ClassVar

import reflex as rx


class MagicBentoCard(rx.Component):
    """Interactive bento card."""

    library = "$/public/MagicBento"
    tag = "MagicBentoCard"

    lib_dependencies: ClassVar[list[str] ]= ["motion@11.15.0"]

    # Component props
    spotlight_radius: rx.Var[int] = 60
    enable_tilt: rx.Var[bool] = True
    enable_magnetism: rx.Var[bool] = True


class MagicBento(rx.Component):
    """Bento grid container."""

    library = "$/public/MagicBento"
    tag = "MagicBento"

    lib_dependencies: ClassVar[list[str] ]= ["motion@11.15.0"]

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
    """Create an interactive magic bento card."""
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
    """Create a magic bento grid container."""
    return MagicBento.create(
        *children,
        columns=columns,
        gap=gap,
        **props,
    )
