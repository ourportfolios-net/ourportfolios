"""Surface, card, form, and button style tokens."""

from __future__ import annotations

from ..tokens import APP_BG, APP_PANEL_BG, APP_SURFACE_BG
from .colors import TEXT_PURPLE, purple, white


CARD_BG = white(0.03)
CARD_BORDER = f"1px solid {white(0.07)}"

SURFACE_BG = white(0.025)
SURFACE_BORDER = f"1px solid {white(0.05)}"

SUBTLE_BG = white(0.035)
SUBTLE_BORDER = f"1px solid {white(0.07)}"

DIVIDER = white(0.05)
SKELETON_BG = white(0.06)

PAGE_BG = APP_BG
MODAL_BG = APP_SURFACE_BG
TABLE_BG = APP_PANEL_BG


CARD_STYLE = {
    "background": CARD_BG,
    "border": CARD_BORDER,
    "border_radius": "0.875rem",
    "padding": "1.5rem",
    "min_height": "15rem",
}

CARD_HOVER_STYLE = {
    "transition": "all 0.15s ease",
    "_hover": {
        "background": white(0.055),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

HUB_CARD_STYLE = {
    **CARD_STYLE,
    **CARD_HOVER_STYLE,
    "position": "relative",
    "overflow": "hidden",
    "min_height": "26.25rem",
}

SURFACE_CARD_STYLE = {
    "padding": "0.75rem",
    "border_radius": "0.625rem",
    "background": SURFACE_BG,
    "border": SURFACE_BORDER,
    "width": "100%",
}

PREVIEW_BOX_STYLE = {
    "padding": "0.75rem",
    "border_radius": "0.625rem",
    "background": white(0.02),
    "border": f"1px solid {white(0.04)}",
    "width": "100%",
    "overflow": "hidden",
}


INPUT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.625rem",
    "color": "white",
    "width": "100%",
    "_placeholder": {"color": white(0.2)},
    "_focus": {
        "border_color": purple(0.4),
        "box_shadow": f"0 0 0 0.1875rem {purple(0.07)}",
        "outline": "none",
    },
}

SELECT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.625rem",
    "color": "white",
    "width": "100%",
    "cursor": "pointer",
}

LABEL_STYLE = {
    "font_size": "0.625rem",
    "font_weight": "700",
    "color": white(0.35),
    "letter_spacing": "0.08em",
    "text_transform": "uppercase",
}

SEARCH_ICON_STYLE = {
    "position": "absolute",
    "left": "0.625rem",
    "top": "50%",
    "transform": "translateY(-50%)",
    "pointer_events": "none",
}

SEARCH_INPUT_STYLE = {
    **INPUT_STYLE,
    "padding_left": "2rem",
    "width": "clamp(12rem, 18vw, 20rem)",
}


BTN_PURPLE = {
    "background": purple(0.15),
    "border": f"1px solid {purple(0.35)}",
    "border_radius": "0.5625rem",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "cursor": "pointer",
    "_hover": {"background": purple(0.22)},
    "transition": "all 0.15s ease",
}

BTN_PURPLE_SM = {**BTN_PURPLE, "border_radius": "0.4375rem"}

BTN_GHOST = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.5625rem",
    "color": white(0.45),
    "cursor": "pointer",
    "_hover": {"background": white(0.07), "color": "white"},
    "transition": "all 0.15s ease",
}

BTN_GHOST_SM = {**BTN_GHOST, "border_radius": "0.4375rem"}
BTN_GHOST_XS = {**BTN_GHOST, "border_radius": "0.375rem"}

BTN_COMPARE = {
    **BTN_GHOST_XS,
    "color": purple(0.55),
    "_hover": {
        "background": purple(0.1),
        "color": purple(0.9),
        "border_color": purple(0.3),
    },
}

BTN_SECONDARY = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": "0.5rem",
    "color": white(0.6),
    "font_weight": "500",
    "font_size": "0.8125rem",
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

BTN_VIEW_ACTIVE = {
    **BTN_SECONDARY,
    "background": white(0.09),
    "border": f"1px solid {white(0.18)}",
    "color": white(0.9),
    "font_weight": "600",
}

BTN_VIEW_INACTIVE = {**BTN_SECONDARY}

BTN_FILTER_ACTIVE = {
    "background": purple(0.18),
    "border": f"1px solid {purple(0.5)}",
    "border_radius": "0.5rem",
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "font_size": "0.8125rem",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {"background": purple(0.28)},
}

PILL_TOGGLE = {
    "background": white(0.03),
    "border": f"1px solid {white(0.06)}",
    "border_radius": "0.375rem",
    "color": white(0.35),
    "cursor": "pointer",
    "transition": "all 0.15s ease",
    "_hover": {"background": white(0.06), "color": white(0.7)},
}

PILL_TOGGLE_ACTIVE = {
    "background": white(0.1),
    "border": f"1px solid {white(0.18)}",
    "border_radius": "0.375rem",
    "color": "white",
    "cursor": "pointer",
    "transition": "all 0.15s ease",
}

CHIP_STYLE = {
    "border_radius": "0.375rem",
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "height": "1.75rem",
    "transition": "all 0.15s ease",
    "_hover": {"background": white(0.09), "border_color": white(0.18)},
}

MODAL_PANEL_STYLE = {
    "background": MODAL_BG,
    "border": f"1px solid {white(0.08)}",
    "border_radius": "0.875rem",
}

FLEX_COL_FILL = {
    "flex": "1",
    "display": "flex",
    "flex_direction": "column",
    "min_height": "0",
}


CARD_HOVER = CARD_HOVER_STYLE
DECISION_HUB_HOVER = {}
