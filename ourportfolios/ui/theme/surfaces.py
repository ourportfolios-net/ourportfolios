"""Surface, card, form, and button style tokens."""

from __future__ import annotations

from ourportfolios.ui.theme.colors import TEXT_PURPLE, purple, white
from ourportfolios.ui.tokens import (
    APP_BG,
    APP_PANEL_BG,
    APP_SURFACE_BG,
    RADIUS_2XS,  # noqa: F401  # re-exported for other modules
    RADIUS_4XS,  # noqa: F401  # re-exported for other modules
    RADIUS_BUTTON,
    RADIUS_CARD,
    RADIUS_INPUT,
    RADIUS_PILL,
    RADIUS_SURFACE,  # noqa: F401  # re-exported for other modules
    TRANS_DEFAULT,
)

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
    "border_radius": RADIUS_CARD,
    "padding": "1.5rem",
    "min_height": "15rem",
}

CARD_HOVER_STYLE = {
    "transition": TRANS_DEFAULT,
    "_hover": {
        "background": white(0.055),
        "border_color": white(0.13),
        "transform": "translateY(-1px)",
    },
}

PREVIEW_BOX_STYLE = {
    "padding": "0.75rem",
    "border_radius": RADIUS_INPUT,
    "background": white(0.02),
    "border": f"1px solid {white(0.04)}",
    "width": "100%",
    "overflow": "hidden",
}


INPUT_STYLE = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": RADIUS_INPUT,
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
    "border_radius": RADIUS_INPUT,
    "color": "white",
    "width": "100%",
    "cursor": "pointer",
}

LABEL_STYLE = {
    "font_size": "0.625rem",
    "color": white(0.35),
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


BUTTON_PURPLE = {
    "background": purple(0.15),
    "border": f"1px solid {purple(0.35)}",
    "border_radius": RADIUS_BUTTON,
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "cursor": "pointer",
    "_hover": {"background": purple(0.22)},
    "transition": TRANS_DEFAULT,
}

BUTTON_PURPLE_SM = {**BUTTON_PURPLE, "border_radius": RADIUS_PILL}

BUTTON_GHOST = {
    "background": white(0.04),
    "border": f"1px solid {white(0.08)}",
    "border_radius": RADIUS_BUTTON,
    "color": white(0.45),
    "cursor": "pointer",
    "_hover": {"background": white(0.07), "color": "white"},
    "transition": TRANS_DEFAULT,
}

BUTTON_GHOST_SM = {**BUTTON_GHOST, "border_radius": RADIUS_PILL}
BUTTON_GHOST_XS = BUTTON_GHOST_SM

BUTTON_COMPARE = {
    **BUTTON_GHOST_XS,
    "color": purple(0.55),
    "_hover": {
        "background": purple(0.1),
        "color": purple(0.9),
        "border_color": purple(0.3),
    },
}

BUTTON_SECONDARY = {
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "border_radius": RADIUS_BUTTON,
    "color": white(0.6),
    "font_weight": "500",
    "font_size": "0.8125rem",
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {
        "background": white(0.09),
        "color": white(0.9),
        "border_color": white(0.18),
    },
}

BUTTON_SECONDARY_ACTIVE = {
    **BUTTON_SECONDARY,
    "background": white(0.09),
    "border": f"1px solid {white(0.18)}",
    "color": white(0.9),
    "font_weight": "600",
}

BUTTON_FILTER_ACTIVE = {
    "background": purple(0.18),
    "border": f"1px solid {purple(0.5)}",
    "border_radius": RADIUS_BUTTON,
    "color": TEXT_PURPLE,
    "font_weight": "600",
    "font_size": "0.8125rem",
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": purple(0.28)},
}

PILL_TOGGLE = {
    "background": white(0.03),
    "border": f"1px solid {white(0.06)}",
    "border_radius": RADIUS_PILL,
    "color": white(0.35),
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.06), "color": white(0.7)},
}

PILL_TOGGLE_ACTIVE = {
    "background": white(0.1),
    "border": f"1px solid {white(0.18)}",
    "border_radius": RADIUS_PILL,
    "color": "white",
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
}

CHIP_STYLE = {
    "border_radius": RADIUS_PILL,
    "background": white(0.05),
    "border": f"1px solid {white(0.1)}",
    "height": "1.75rem",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.09), "border_color": white(0.18)},
}

MODAL_PANEL_STYLE = {
    "background": MODAL_BG,
    "border": f"1px solid {white(0.08)}",
    "border_radius": RADIUS_CARD,
}
