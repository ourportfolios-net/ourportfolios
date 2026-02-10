"""Interactive bento card components for the landing page."""

import reflex as rx


class TransparencyCard(rx.Component):
    """Card that fades from opaque to transparent on hover."""

    library = "$/public/BentoCards"
    tag = "TransparencyCard"
    lib_dependencies: list[str] = ["motion@11.15.0"]


class FocusedCard(rx.Component):
    """Card with text focus/blur effect on hover."""

    library = "$/public/BentoCards"
    tag = "FocusedCard"
    lib_dependencies: list[str] = ["motion@11.15.0"]


class ConcisenessCard(rx.Component):
    """Card with scroll-to-reveal effect on hover."""

    library = "$/public/BentoCards"
    tag = "ConcisenessCard"
    lib_dependencies: list[str] = ["motion@11.15.0"]


class ReliabilityCard(rx.Component):
    """Card with sequential verification checkmark animation."""

    library = "$/public/BentoCards"
    tag = "ReliabilityCard"
    lib_dependencies: list[str] = ["motion@11.15.0"]


class InstructivenessCard(rx.Component):
    """Card with floating concept badges on hover."""

    library = "$/public/BentoCards"
    tag = "InstructivenessCard"
    lib_dependencies: list[str] = ["motion@11.15.0"]


def transparency_card(**props) -> rx.Component:
    """Create a transparency interactive bento card."""
    return TransparencyCard.create(**props)


def focused_card(**props) -> rx.Component:
    """Create a focused interactive bento card."""
    return FocusedCard.create(**props)


def conciseness_card(**props) -> rx.Component:
    """Create a conciseness interactive bento card."""
    return ConcisenessCard.create(**props)


def reliability_card(**props) -> rx.Component:
    """Create a reliability interactive bento card."""
    return ReliabilityCard.create(**props)


def instructiveness_card(**props) -> rx.Component:
    """Create an instructiveness interactive bento card."""
    return InstructivenessCard.create(**props)
