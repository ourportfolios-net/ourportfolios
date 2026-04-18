"""CardSwap auto-rotating card stack."""


import reflex as rx


class CardSwapComponent(rx.Component):
    """CardSwap container with GSAP animations."""

    library = "$/public/CardSwap"
    tag = "CardSwap"
    is_default = True

    lib_dependencies: list[str] = ["gsap@3.12.5"]

    # Component props
    width: rx.Var[int]
    height: rx.Var[int]
    card_distance: rx.Var[int]
    vertical_distance: rx.Var[int]
    delay: rx.Var[int]
    pause_on_hover: rx.Var[bool]
    skew_amount: rx.Var[int]
    easing: rx.Var[str]


class CardComponent(rx.Component):
    """Card in the CardSwap stack."""

    library = "$/public/CardSwap"
    tag = "Card"

    custom_class: rx.Var[str]


card_swap = CardSwapComponent.create
card = CardComponent.create
