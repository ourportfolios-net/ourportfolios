"""Landing page module."""

from ourportfolios.pages.landing.components.card_swap import (
    CardComponent,
    CardSwapComponent,
    card,
    card_swap,
)
from ourportfolios.pages.landing.components.magic_bento import (
    MagicBentoCard,
    magic_bento,
    magic_bento_card,
)
from ourportfolios.pages.landing.components.plasma import Plasma, plasma
from ourportfolios.pages.landing.components.shiny_text import ShinyText, shiny_text
from ourportfolios.pages.landing.index import index

__all__ = [
    "CardComponent",
    "CardSwapComponent",
    "MagicBentoCard",
    "Plasma",
    "ShinyText",
    "card",
    "card_swap",
    "index",
    "magic_bento",
    "magic_bento_card",
    "plasma",
    "shiny_text",
]
