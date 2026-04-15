"""Color primitives and semantic color tokens."""

from __future__ import annotations


def purple(a: float) -> str:
    return f"rgba(139, 92, 246, {a})"


def blue(a: float) -> str:
    return f"rgba(59, 130, 246, {a})"


def green(a: float) -> str:
    return f"rgba(16, 185, 129, {a})"


def red(a: float) -> str:
    return f"rgba(239, 68, 68, {a})"


def white(a: float) -> str:
    return f"rgba(255, 255, 255, {a})"


def black(a: float) -> str:
    return f"rgba(0, 0, 0, {a})"


def indigo(a: float) -> str:
    return f"rgba(99, 102, 241, {a})"


GREEN_LABEL = green(1.0)
RED_LABEL = red(1.0)

GREEN_FILL = green(0.5)
RED_FILL = red(0.5)

GREEN_FADE = green(0.08)
RED_FADE = red(0.08)

GREEN_BORDER = green(0.12)
RED_BORDER = red(0.12)

GREEN_BG = green(0.05)
RED_BG = red(0.05)


TOOLTIP_CURSOR = {"fill": white(0.06)}
TOOLTIP_CONTENT_STYLE = {
    "backgroundColor": "rgba(14, 14, 18, 0.95)",
    "border": f"1px solid {white(0.08)}",
    "borderRadius": "0.5rem",
    "padding": "0.375rem 0.625rem",
}
TOOLTIP_WRAPPER_STYLE = {"zIndex": "9999"}


ERROR_COLOR = "rgba(255, 100, 100, 0.8)"
ERROR_BORDER = "1px solid rgba(255, 80, 80, 0.5)"
ERROR_SHADOW = "0 0 0 0.1875rem rgba(255, 80, 80, 0.08)"
DELETE_HOVER = "rgba(236, 93, 94, 0.85)"


TEXT_PRIMARY = "white"
TEXT_SECONDARY = white(0.5)
TEXT_TERTIARY = white(0.3)
TEXT_MUTED = white(0.2)
TEXT_PURPLE = "#c4b5fd"
TEXT_ACCENT = "#a78bfa"

TEXT_TRUNCATE = {
    "white_space": "nowrap",
    "overflow": "hidden",
    "text_overflow": "ellipsis",
}
