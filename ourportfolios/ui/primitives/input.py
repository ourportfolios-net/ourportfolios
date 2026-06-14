"""Input primitives for consistent form controls."""

from __future__ import annotations

from typing import cast

import reflex as rx

from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import (
    INPUT_STYLE,
    SEARCH_ICON_STYLE,
    SEARCH_INPUT_STYLE,
    SELECT_STYLE,
)
from ourportfolios.ui.tokens import FONT_LABEL, FONT_SM


def text_input(
    *,
    placeholder: str = "",
    value: rx.Var[str] | str | None = None,
    on_change: object = None,
    **props: object,
) -> rx.Component:
    """Create a standard text input with consistent styling.

    Args:
        placeholder: Placeholder text.
        value: Reflex Var or value binding.
        on_change: Change event handler.
        **props: Additional Reflex input props.

    """
    return rx.input(
        **cast("dict", {
            "placeholder": placeholder,
            "value": value,
            "on_change": on_change,
            "style": INPUT_STYLE,
            **props,
        }),
    )


def search_input(
    *,
    placeholder: str = "Search...",
    value: rx.Var[str] | str | None = None,
    on_change: object = None,
    **props: object,
) -> rx.Component:
    """Search input with left padding for search icon.

    Args:
        placeholder: Placeholder text.
        value: Reflex Var or value binding.
        on_change: Change event handler.
        **props: Additional Reflex input props.

    """
    return rx.input(
        **cast("dict", {
            "placeholder": placeholder,
            "value": value,
            "on_change": on_change,
            "style": SEARCH_INPUT_STYLE,
            **props,
        }),
    )


def search_input_with_icon(
    *,
    placeholder: str = "Search...",
    value: rx.Var[str] | str | None = None,
    on_change: object = None,
    icon: str = "search",
    custom_attrs: dict[str, str | rx.Var[str]] | None = None,
    **props: object,
) -> rx.Component:
    """Create a search input with icon slot.

    Args:
        placeholder: Placeholder text.
        value: Reflex Var or value binding.
        on_change: Change event handler.
        icon: Icon name for the slot.
        custom_attrs: Custom HTML attributes.
        **props: Additional Reflex input props (on_blur, on_focus, etc.).

    """
    return rx.input(
        rx.input.slot(rx.icon(tag=icon, size=16)),
        **cast("dict", {
            "placeholder": placeholder,
            "value": value,
            "on_change": on_change,
            "custom_attrs": custom_attrs,
            "style": {**SEARCH_INPUT_STYLE, "padding_left": "0"},
            **props,
        }),
    )


def select_input(**props: object) -> rx.Component:
    """Select/dropdown input with consistent styling.

    Args:
        **props: Additional Reflex select props.

    """
    return rx.select(
        **cast("dict", {
            "style": SELECT_STYLE,
            **props,
        }),
    )


def text_area_input(
    *,
    placeholder: str = "",
    value: rx.Var[str] | str | None = None,
    on_change: object = None,
    rows: int = 4,
    **props: object,
) -> rx.Component:
    """Textarea input with consistent styling.

    Args:
        placeholder: Placeholder text.
        value: Reflex Var or value binding.
        on_change: Change event handler.
        rows: Number of visible rows.
        **props: Additional Reflex input props.

    """
    return rx.text_area(
        **cast("dict", {
            "placeholder": placeholder,
            "value": value,
            "on_change": on_change,
            "rows": str(rows),
            "style": INPUT_STYLE,
            **props,
        }),
    )


def search_icon(**props: object) -> rx.Component:
    """Search icon positioned absolutely inside an input container.

    Args:
        **props: Additional Reflex icon props.

    """
    return rx.icon(
        "search",
        **cast("dict", {
            "size": 14,
            "color": white(0.25),
            "style": SEARCH_ICON_STYLE,
            **props,
        }),
    )


def form_field(
    label: str,
    input_component: rx.Component,
    *,
    error: str = "",
    **props: object,
) -> rx.Component:
    """Form field with label and optional error message.

    Args:
        label: Field label text.
        input_component: The input component to render.
        error: Optional error message.
        **props: Additional Reflex component props.

    """
    return rx.vstack(
        _label_text(label),
        input_component,
        rx.cond(
            error != "",
            rx.text(error, font_size=FONT_SM, color="rgba(255, 100, 100, 0.8)"),
            rx.fragment(),
        ),
        **cast("dict", {
            "spacing": "1",
            "align": "start",
            "width": "100%",
            **props,
        }),
    )


def _label_text(text: str | rx.Var[str], **props: object) -> rx.Component:
    """Form label text (private helper for form_field).

    Args:
        text: Label text or Reflex Var.
        **props: Additional Reflex text props.

    """
    return rx.text(
        text,
        **cast("dict", {
            "font_size": FONT_LABEL,
            "color": white(0.35),
            **props,
        }),
    )
