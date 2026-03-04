"""Centralized style tokens and helpers for consistent UI."""

import reflex as rx

# ── Colors ────────────────────────────────────────────────────────────────────


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


# ── Semantic color aliases ────────────────────────────────────────────────────

# Use green/red helpers for positive/negative
GREEN_LABEL = green(1.0)  # "rgba(16, 185, 129, 1.0)"  — bright green text
RED_LABEL = red(1.0)

GREEN_FILL = green(0.5)
RED_FILL = red(0.5)

GREEN_FADE = green(0.08)
RED_FADE = red(0.08)

GREEN_BORDER = green(0.12)
RED_BORDER = red(0.12)

GREEN_BG = green(0.05)
RED_BG = red(0.05)


# ── Recharts ──────────────────────────────────────────────────────────────────

TOOLTIP_CURSOR = {"fill": white(0.06)}
TOOLTIP_CONTENT_STYLE = {
    "backgroundColor": "rgba(14, 14, 18, 0.95)",
    "border": f"1px solid {white(0.08)}",
    "borderRadius": "8px",
    "padding": "6px 10px",
}
TOOLTIP_WRAPPER_STYLE = {"zIndex": "9999"}


# ── Error / danger ────────────────────────────────────────────────────────────

ERROR_COLOR = "rgba(255, 100, 100, 0.8)"
ERROR_BORDER = "1px solid rgba(255, 80, 80, 0.5)"
ERROR_SHADOW = "0 0 0 3px rgba(255, 80, 80, 0.08)"
DELETE_HOVER = "rgba(236, 93, 94, 0.85)"


# ── Text tokens ───────────────────────────────────────────────────────────────

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


# ── Surfaces ──────────────────────────────────────────────────────────────────

CARD_BG = white(0.03)
CARD_BORDER = f"1px solid {white(0.07)}"

SURFACE_BG = white(0.025)
SURFACE_BORDER = f"1px solid {white(0.05)}"

SUBTLE_BG = white(0.035)
SUBTLE_BORDER = f"1px solid {white(0.07)}"

DIVIDER = white(0.05)
SKELETON_BG = white(0.06)

PAGE_BG = "#090909"
MODAL_BG = "#111111"
TABLE_BG = "#0d0d0d"


# ── Card styles ───────────────────────────────────────────────────────────────

CARD_STYLE = {
    "background": CARD_BG,
    "border": CARD_BORDER,
    "border_radius": "14px",
    "padding": "1.5rem",
    "min_height": "240px",
}

# Standard hover applied to ALL cards (hub cards, glass cards, framework card)
CARD_HOVER_STYLE = {
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.055),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

# Hub card base = CARD_STYLE + hover + extra layout props
HUB_CARD_STYLE = {
    **CARD_STYLE,
    **CARD_HOVER_STYLE,
    "position": "relative",
    "overflow": "hidden",
    "height": "420px",
}

SURFACE_CARD_STYLE = {
    "padding": "0.75rem",
    "border_radius": "10px",
    "background": SURFACE_BG,
    "border": SURFACE_BORDER,
    "width": "100%",
}

# Preview box inside hub cards
PREVIEW_BOX_STYLE = {
    "padding": "0.75rem",
    "border_radius": "10px",
    "background": white(0.02),
    "border": f"1px solid {white(0.04)}",
    "width": "100%",
    "overflow": "hidden",
}


# ── Form controls ─────────────────────────────────────────────────────────────

INPUT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "_placeholder": {"color": white(0.2)},
    "_focus": {
        "border_color": purple(0.4),
        "box_shadow": f"0 0 0 3px {purple(0.07)}",
        "outline": "none",
    },
}

SELECT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "cursor": "pointer",
}

LABEL_STYLE = {
    "font_size": "10px",
    "font_weight": "700",
    "color": white(0.35),
    "letter_spacing": "0.08em",
    "text_transform": "uppercase",
}

SEARCH_ICON_STYLE = {
    "position": "absolute",
    "left": "10px",
    "top": "50%",
    "transform": "translateY(-50%)",
    "pointer_events": "none",
}

SEARCH_INPUT_STYLE = {
    **INPUT_STYLE,
    "padding_left": "2rem",
    "width": "280px",
}


# ── Dialog / modal buttons ────────────────────────────────────────────────────

BTN_PURPLE = {
    "background": purple(0.15),
    "border": f"1px solid {purple(0.35)}",
    "border_radius": "9px",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "cursor": "pointer",
    "_hover": {"background": purple(0.22)},
    "transition": "all 0.15s ease",
}

BTN_PURPLE_SM = {**BTN_PURPLE, "border_radius": "7px"}

BTN_GHOST = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "9px",
    "color": white(0.45),
    "cursor": "pointer",
    "_hover": {"background": white(0.07), "color": "white"},
    "transition": "all 0.15s ease",
}

BTN_GHOST_SM = {**BTN_GHOST, "border_radius": "7px"}
BTN_GHOST_XS = {**BTN_GHOST, "border_radius": "6px"}

BTN_COMPARE = {
    **BTN_GHOST_XS,
    "color": purple(0.55),
    "_hover": {
        "background": purple(0.1),
        "color": purple(0.9),
        "border_color": purple(0.3),
    },
}

# Secondary (icon+label) – the standard toolbar button look
BTN_SECONDARY = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": "8px",
    "color": white(0.6),
    "font_weight": "500",
    "font_size": "13px",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.09),
        "color": white(0.9),
        "border_color": white(0.18),
    },
}

BTN_SECONDARY_ACTIVE = {
    **BTN_SECONDARY,
    "background": white(0.09),
    "border": f"1px solid {white(0.18)}",
    "color": white(0.9),
    "font_weight": "600",
}

# View toggle – active/inactive for Board/Compare switches
BTN_VIEW_ACTIVE = {
    **BTN_SECONDARY,
    "background": white(0.09),
    "border": f"1px solid {white(0.18)}",
    "color": white(0.9),
    "font_weight": "600",
}

BTN_VIEW_INACTIVE = {
    **BTN_SECONDARY,
}

BTN_FILTER_ACTIVE = {
    "background": purple(0.18),
    "border": f"1px solid {purple(0.5)}",
    "border_radius": "8px",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "font_size": "13px",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {"background": purple(0.28)},
}

# Pill toggle – used for view/mode switches (matches price_chart.py _chart_type_toggle)
PILL_TOGGLE = {
    "background": white(0.03),
    "border": f"1px solid {white(0.06)}",
    "border_radius": "6px",
    "color": white(0.35),
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {"background": white(0.06), "color": white(0.7)},
}

PILL_TOGGLE_ACTIVE = {
    "background": white(0.1),
    "border": f"1px solid {white(0.18)}",
    "border_radius": "6px",
    "color": "white",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
}

CHIP_STYLE = {
    "border_radius": "6px",
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "height": "28px",
    "transition": "all 0.15s ease",
    "_hover": {"background": white(0.09), "border_color": white(0.18)},
}

MODAL_PANEL_STYLE = {
    "background": MODAL_BG,
    "border": f"1px solid {white(0.08)}",
    "border_radius": "14px",
}

FLEX_COL_FILL = {
    "flex": "1",
    "display": "flex",
    "flex_direction": "column",
    "min_height": "0",
}


# ── Card CTA button components ────────────────────────────────────────────────


def accent_btn(
    label: str,
    icon: str = "arrow-right",
    href: str | None = None,
    on_click=None,
    icon_left: bool = False,
) -> rx.Component:
    """Small rounded ghost CTA used at the bottom-right of cards.

    Rest state:  white(0.04) bg, white(0.09) border, white(0.65) text, white(0.45) icon.
    Hover state: lightens bg + border, same as card hover language — no purple.
    """
    icon_el = rx.icon(icon, size=12, color=white(0.5))
    label_el = rx.text(label, size="1", weight="medium", color=white(0.65))
    children = [icon_el, label_el] if icon_left else [label_el, icon_el]

    inner = rx.box(
        rx.hstack(*children, spacing="1", align="center"),
        padding="0.35em 0.75em",
        background=white(0.04),
        border=f"1px solid {white(0.09)}",
        border_radius="8px",
        transition="all 0.15s ease",
        _hover={"background": white(0.09), "border_color": white(0.2)},
        cursor="pointer",
        align_self="flex-end",
        position="relative",
        z_index="2",
        display="inline-flex",
    )
    if href:
        return rx.link(
            inner,
            href=href,
            underline="none",
            align_self="flex-end",
            position="relative",
            z_index="2",
        )
    if on_click:
        return rx.box(
            inner,
            on_click=on_click,
            cursor="pointer",
            align_self="flex-end",
            position="relative",
            z_index="2",
        )
    return inner


def ghost_btn(
    label: str,
    icon: str = "arrow-right",
    href: str | None = None,
    on_click=None,
) -> rx.Component:
    """Alias of accent_btn — kept for call-sites that use the ghost variant."""
    return accent_btn(label, icon=icon, href=href, on_click=on_click)


# ── Icon box helper ───────────────────────────────────────────────────────────

_ICON_COLORS = {
    "purple": (purple(0.12), purple(0.25), "rgba(167, 139, 250, 0.9)"),
    "blue": (blue(0.12), blue(0.25), "rgba(96, 165, 250, 0.9)"),
    "green": (green(0.12), green(0.25), "rgba(52, 211, 153, 0.9)"),
    "indigo": (indigo(0.1), indigo(0.2), "rgba(129, 140, 248, 0.85)"),
}


def icon_box(icon_name: str, color: str = "purple", size: int = 16) -> rx.Component:
    """Renders a coloured square icon box — replaces repeated inline rx.box(...) blocks."""
    bg, border, icon_color_val = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return rx.box(
        rx.icon(icon_name, size=size, color=icon_color_val),
        background=bg,
        border=f"1px solid {border}",
        border_radius="10px",
        padding="9px",
        display="flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def icon_box_style(
    color: str = "purple", size: str = "40px", radius: str = "10px"
) -> dict:
    """Returns a style dict for cases where a component helper isn't suitable."""
    bg, border, _ = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return {
        "width": size,
        "height": size,
        "border_radius": radius,
        "background": bg,
        "border": f"1px solid {border}",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "flex_shrink": "0",
    }


def icon_color(color: str = "purple") -> str:
    _, _, c = _ICON_COLORS.get(color, _ICON_COLORS["purple"])
    return c


# ── Misc helpers ──────────────────────────────────────────────────────────────


def glow_orb_style(color: str = "purple") -> dict:
    colors = {"purple": purple(0.07), "blue": blue(0.07), "green": green(0.07)}
    return {
        "position": "absolute",
        "right": "-2rem",
        "top": "-2rem",
        "width": "130px",
        "height": "130px",
        "background": colors.get(color, colors["purple"]),
        "filter": "blur(50px)",
        "border_radius": "9999px",
        "pointer_events": "none",
    }


def skeleton_box_style(
    width: str, height: str, radius: str = "4px", opacity: float = 0.06
) -> dict:
    return {
        "width": width,
        "height": height,
        "border_radius": radius,
        "background": f"rgba(255, 255, 255, {opacity})",
        "flex_shrink": "0",
    }


def overlay_style(is_active) -> dict:
    """Absolute-positioned layer toggled via opacity."""
    return {
        "opacity": rx.cond(is_active, "1", "0"),
        "pointer_events": rx.cond(is_active, "auto", "none"),
        "transition": "opacity 0.15s ease",
        "position": "absolute",
        "inset": "0",
    }


# ── Landing page ──────────────────────────────────────────────────────────────

LANDING_CARD = {
    "background": "transparent",
    "backdrop_filter": "blur(20px)",
    "border": f"1px solid {white(0.07)}",
    "border_radius": "1.5rem",
    "display": "flex",
    "flex_direction": "column",
}

LANDING_METRIC_BOX = {
    "flex": "1",
    "padding": "0.875rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.625rem",
}

LANDING_CHART_BOX = {
    "flex": "1",
    "padding": "0.75rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.07)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW_SELECTED = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": purple(0.1),
    "border": f"1px solid {purple(0.25)}",
    "border_radius": "0.75rem",
}


# ── Table / comparison ────────────────────────────────────────────────────────

TABLE_CELL_BORDER = f"1px solid {white(0.04)}"

TICKER_CARD_STYLE = {
    "transition": "all 0.2s ease",
    "marginLeft": "0.6em",
    "_hover": {"marginLeft": "0"},
}

# kept for backward compat
CARD_HOVER = CARD_HOVER_STYLE
DECISION_HUB_HOVER = {}
