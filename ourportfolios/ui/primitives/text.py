"""Text primitives for consistent typography."""

from __future__ import annotations

from typing import cast

import reflex as rx

from ourportfolios.ui.theme.colors import (
    TEXT_ACCENT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_TRUNCATE,
    white,
)
from ourportfolios.ui.tokens import (
    FONT_BASE,
    FONT_LABEL,
    LETTER_NORMAL,
    LETTER_SNUG,
    LETTER_TIGHT,
    TRANS_COLOR,
    WEIGHT_BOLD,
    WEIGHT_EXTRABOLD,
    WEIGHT_REGULAR,
    WEIGHT_SEMIBOLD,
)


def heading(
    text: str | rx.Var[str],
    level: int = 1,
    **props: object,
) -> rx.Component:
    """Heading text with consistent sizing.

    Type scale (Reflex size → rem):
        size 7 ≈ 3rem, size 6 ≈ 2.25rem, size 4 ≈ 1.5rem

    Levels:
        1: Page title (size 7, weight 750, letter-spacing -0.03em)
        2: Section title (size 6, weight 650, letter-spacing -0.02em)
        3: Subsection title (size 4, semibold, letter-spacing -0.01em)

    Args:
        text: Heading text or Reflex Var.
        level: Heading level (1-3).
        **props: Additional Reflex text props.

    """
    sizes = {1: "7", 2: "6", 3: "4"}
    font_weights = {1: WEIGHT_EXTRABOLD, 2: WEIGHT_BOLD, 3: WEIGHT_SEMIBOLD}
    letter_spacings = {1: LETTER_TIGHT, 2: LETTER_SNUG, 3: LETTER_NORMAL}
    size = sizes.get(level, "6")
    font_weight = font_weights.get(level, "bold")
    letter_spacing = letter_spacings.get(level, "0")
    return rx.heading(
        text,
        **{
            "size": size,
            "font_weight": font_weight,
            "letter_spacing": letter_spacing,
            "color": TEXT_PRIMARY,
            **props,
        },
    )


def subheading(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Subheading text — smaller than heading, used for card titles.

    Args:
        text: Subheading text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{
            "size": "3",
            "weight": "medium",
            "color": white(0.7),
            **props,
        },
    )


def body_text(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Body text for general content.

    Args:
        text: Body text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{"size": "2", "color": white(0.6), **props},
    )


def label_text(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Small label text for form labels and metadata.

    Args:
        text: Label text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{"font_size": FONT_LABEL, "color": white(0.35), **props},
    )


def muted_text(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Muted text for secondary/descriptive content.

    Args:
        text: Muted text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{"size": "2", "color": TEXT_MUTED, **props},
    )


def accent_text(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Accent-colored text (purple/violet).

    Args:
        text: Accent text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{"color": TEXT_ACCENT, **props},
    )


def truncated_text(
    text: str | rx.Var[str],
    max_width: str | None = None,
    **props: object,
) -> rx.Component:
    """Text with ellipsis overflow truncation.

    Args:
        text: Text or Reflex Var.
        max_width: Optional max-width constraint.
        **props: Additional Reflex text props.

    """
    base_style: dict[str, object] = dict(TEXT_TRUNCATE)
    if max_width:
        base_style["max_width"] = max_width
    if "style" in props:
        style_val = props.pop("style")
        base_style.update(cast("dict[str, object]", style_val))
    return rx.text(text, style=base_style, **props)


def nav_link_text(
    text: str | rx.Var[str],
    **props: object,
) -> rx.Component:
    """Navigation link text with hover transition.

    Args:
        text: Link text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **{
            "font_size": FONT_BASE,
            "font_weight": WEIGHT_REGULAR,
            "color": white(0.5),
            "text_decoration": "none",
            "_hover": {"color": "white"},
            "transition": TRANS_COLOR,
            **props,
        },
    )


def badge_text(
    text: str | rx.Var[str],
    scheme: str = "gray",
    **props: object,
) -> rx.Component:
    """Badge component with consistent styling.

    Args:
        text: Badge text or Reflex Var.
        scheme: Color scheme (green, red, gray, violet).
        **props: Additional Reflex badge props.

    """
    return rx.badge(
        text,
        **{
            "color_scheme": scheme,
            "variant": "soft",
            "size": "1",
            **props,
        },
    )
