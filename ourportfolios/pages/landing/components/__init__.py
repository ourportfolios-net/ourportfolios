"""Landing page components."""

from .plasma import plasma, Plasma
from .shiny_text import shiny_text, ShinyText
from .magic_bento import magic_bento, magic_bento_card, MagicBentoCard
from .card_swap import card_swap, card, CardSwapComponent, CardComponent
from .scroll_reveal import scroll_reveal, ScrollRevealComponent
from .badge_button import badge_button
from .bento_cards import (
    transparency_card,
    focused_card,
    conciseness_card,
    reliability_card,
    instructiveness_card,
    TransparencyCard,
    FocusedCard,
    ConcisenessCard,
    ReliabilityCard,
    InstructivenessCard,
)

__all__ = [
    "plasma",
    "Plasma",
    "shiny_text",
    "ShinyText",
    "magic_bento",
    "magic_bento_card",
    "MagicBentoCard",
    "card_swap",
    "card",
    "CardSwapComponent",
    "CardComponent",
    "scroll_reveal",
    "ScrollRevealComponent",
    "badge_button",
    "transparency_card",
    "focused_card",
    "conciseness_card",
    "reliability_card",
    "instructiveness_card",
    "TransparencyCard",
    "FocusedCard",
    "ConcisenessCard",
    "ReliabilityCard",
    "InstructivenessCard",
]
