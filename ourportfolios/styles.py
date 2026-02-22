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
TOOLTIP_CURSOR = {"fill": "rgba(255, 255, 255, 0.1)"}
TOOLTIP_CONTENT_STYLE = {
    "backgroundColor": "rgba(0, 0, 0, 0.9)",
    "border": "1px solid #666",
    "borderRadius": "4px",
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

CARD_BG = white(0.025)
CARD_BORDER = f"1px solid {white(0.07)}"
SURFACE_BG = white(0.03)
SURFACE_BORDER = f"1px solid {white(0.05)}"
SUBTLE_BG = white(0.04)
SUBTLE_BORDER = f"1px solid {white(0.09)}"
DIVIDER = white(0.05)
SKELETON_BG = white(0.08)

# ── Common style dicts ────────────────────────────────────────────────────────

INPUT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.09)}",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "_placeholder": {"color": white(0.22)},
    "_focus": {
        "border_color": purple(0.45),
        "box_shadow": f"0 0 0 3px {purple(0.08)}",
        "outline": "none",
    },
}

SELECT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.09)}",
    "border_radius": "10px",
    "color": "white",
    "width": "100%",
    "cursor": "pointer",
}

LABEL_STYLE = {
    "font_size": "11px",
    "font_weight": "600",
    "color": white(0.55),
    "letter_spacing": "0.07em",
    "text_transform": "uppercase",
}

BTN_PURPLE = {
    "background": purple(0.18),
    "border": f"1px solid {purple(0.45)}",
    "border_radius": "10px",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "cursor": "pointer",
    "_hover": {"background": purple(0.28)},
}

BTN_PURPLE_SM = {**BTN_PURPLE, "border_radius": "8px"}

BTN_GHOST = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": "10px",
    "color": white(0.5),
    "cursor": "pointer",
    "_hover": {"background": white(0.09)},
}

BTN_GHOST_SM = {**BTN_GHOST, "border_radius": "8px"}

BTN_GHOST_XS = {**BTN_GHOST, "border_radius": "6px", "color": white(0.7)}

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

DECISION_HUB_HOVER = {
    "_hover": {
        "& > :nth-child(2)": {
            "background": white(0.04),
            "border_color": white(0.05),
        }
    }
}

# ── Helpers ───────────────────────────────────────────────────────────────────

_ICON_COLORS = {
    "purple": (purple(0.2), purple(0.3), "var(--accent-purple)"),
    "blue": (blue(0.2), blue(0.3), "var(--blue-9)"),
    "green": (green(0.2), green(0.3), "var(--green-9)"),
    "indigo": (indigo(0.15), indigo(0.3), "var(--indigo-9)"),
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
    colors = {"purple": purple(0.1), "blue": blue(0.1), "green": green(0.1)}
    return {
        "position": "absolute",
        "right": "-3rem",
        "top": "-3rem",
        "width": "160px",
        "height": "160px",
        "background": colors.get(color, colors["purple"]),
        "filter": "blur(60px)",
        "border_radius": "9999px",
        "transition": "all 0.3s ease",
    }


def skeleton_box_style(
    width: str, height: str, radius: str = "4px", opacity: float = 0.08
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
    "border": f"1px solid {white(0.08)}",
    "border_radius": "1.5rem",
    "display": "flex",
    "flex_direction": "column",
}

LANDING_METRIC_BOX = {
    "flex": "1",
    "padding": "0.875rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.625rem",
}

LANDING_CHART_BOX = {
    "flex": "1",
    "padding": "0.75rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.75rem",
}

LANDING_LIST_ROW_SELECTED = {
    "width": "100%",
    "padding": "1rem 1.25rem",
    "background": purple(0.1),
    "border": f"1px solid {purple(0.3)}",
    "border_radius": "0.75rem",
}

# ── Table / comparison ────────────────────────────────────────────────────────

TABLE_CELL_BORDER = f"1px solid {white(0.04)}"

TICKER_CARD_STYLE = {
    "transition": "all 0.2s ease",
    "marginLeft": "0.6em",
    "_hover": {"marginLeft": "0"},
}
