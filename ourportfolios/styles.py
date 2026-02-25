"""Centralized style tokens and helpers for consistent UI."""

# ── Colors ──────────────────────────────────────────────────────────────────


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


# Recharts tooltip shared styles
TOOLTIP_CURSOR = {"fill": "rgba(255, 255, 255, 0.06)"}
TOOLTIP_CONTENT_STYLE = {
    "backgroundColor": "rgba(14, 14, 18, 0.95)",
    "border": "1px solid rgba(255,255,255,0.08)",
    "borderRadius": "8px",
    "padding": "6px 10px",
}
TOOLTIP_WRAPPER_STYLE = {"zIndex": "9999"}

# Error / danger colours
ERROR_COLOR = "rgba(255, 100, 100, 0.8)"
ERROR_BORDER = "1px solid rgba(255, 80, 80, 0.5)"
ERROR_SHADOW = "0 0 0 3px rgba(255, 80, 80, 0.08)"
DELETE_HOVER = "rgba(236, 93, 94, 0.85)"

TEXT_PRIMARY = "white"
TEXT_SECONDARY = white(0.5)
TEXT_TERTIARY = white(0.3)
TEXT_MUTED = white(0.2)
TEXT_PURPLE = "#c4b5fd"
TEXT_ACCENT = "#a78bfa"

# ── Surfaces ─────────────────────────────────────────────────────────────────

# These match the framework page card exactly
CARD_BG = white(0.03)
CARD_BORDER = f"1px solid {white(0.07)}"
SURFACE_BG = white(0.025)
SURFACE_BORDER = f"1px solid {white(0.05)}"
SUBTLE_BG = white(0.035)
SUBTLE_BORDER = f"1px solid {white(0.07)}"
DIVIDER = white(0.05)
SKELETON_BG = white(0.06)

# ── Common style dicts ────────────────────────────────────────────────────────

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

# ── CARD_STYLE: single source of truth, matches framework page cards exactly ──
CARD_STYLE = {
    "background": CARD_BG,
    "border": CARD_BORDER,
    "border_radius": "14px",
    "padding": "1.5rem",
    "min_height": "240px",
}

SURFACE_CARD_STYLE = {
    "padding": "0.75rem",
    "border_radius": "10px",
    "background": SURFACE_BG,
    "border": SURFACE_BORDER,
    "width": "100%",
}

CARD_HOVER = {
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.045),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

# Kept for backward compat but no longer needed on home cards
DECISION_HUB_HOVER = {}

# ── Helpers ───────────────────────────────────────────────────────────────────

_ICON_COLORS = {
    "purple": (purple(0.1), purple(0.2), "rgba(167, 139, 250, 0.85)"),
    "blue": (blue(0.1), blue(0.2), "rgba(96, 165, 250, 0.85)"),
    "green": (green(0.1), green(0.2), "rgba(52, 211, 153, 0.85)"),
    "indigo": (indigo(0.1), indigo(0.2), "rgba(129, 140, 248, 0.85)"),
}


def icon_box_style(
    color: str = "purple", size: str = "40px", radius: str = "10px"
) -> dict:
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


def glow_orb_style(color: str = "purple") -> dict:
    """Kept for any pages that still use it."""
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
