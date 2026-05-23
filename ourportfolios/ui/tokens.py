"""Centralized UI tokens for layout and scalable page composition."""

from __future__ import annotations

# ── Background Colors ─────────────────────────────────────────────────────────
APP_BG = "#090909"
APP_SURFACE_BG = "#111111"
APP_PANEL_BG = "#0d0d0d"

# ── Page Layout ───────────────────────────────────────────────────────────────
PAGE_MAX_WIDTH = "90rem"
PAGE_EDGE_PADDING = "2rem"
PAGE_VERTICAL_PADDING = "2rem"
SECTION_GAP = "1.25rem"

HOME_CONTENT_WIDTH = "86vw"
HOME_CONTENT_MAX_WIDTH = PAGE_MAX_WIDTH
HOME_PAGE_HORIZONTAL_PADDING = PAGE_EDGE_PADDING
HOME_PAGE_VERTICAL_PADDING = PAGE_VERTICAL_PADDING

# ── Border Radius ─────────────────────────────────────────────────────────────
# Three values only: buttons/pills, inputs/containers, cards/modals
RADIUS_SM = "0.5rem"          # Buttons, pills, badges, chips, avatars, icon boxes
RADIUS_MD = "0.75rem"         # Inputs, metric boxes, nested containers, dropdowns
RADIUS_LG = "0.875rem"        # Cards, modals, section containers

# Semantic aliases
RADIUS_BUTTON = RADIUS_SM
RADIUS_PILL = RADIUS_SM
RADIUS_INPUT = RADIUS_MD
RADIUS_SURFACE = RADIUS_MD
RADIUS_CARD = RADIUS_LG

# ── Spacing / Padding ────────────────────────────────────────────────────────
# Four values only
SPACE_SM = "0.5rem"           # Tight: badge padding, inline gaps
SPACE_MD = "1rem"             # Default: card padding, standard gaps
SPACE_LG = "1.5rem"           # Comfortable: section/modal padding
SPACE_XL = "2rem"             # Large: page-level gaps, empty states

# ── Typography ───────────────────────────────────────────────────────────────
FONT_LABEL = "0.625rem"       # Labels, helper text
FONT_SM = "0.75rem"           # Small text, badges
FONT_BASE = "0.875rem"        # Body text, nav links
FONT_LG = "1rem"              # Large text
FONT_XL = "1.25rem"           # Extra large (menu headings)

WEIGHT_REGULAR = "400"
WEIGHT_MEDIUM = "500"
WEIGHT_SEMIBOLD = "600"
WEIGHT_BOLD = "650"
WEIGHT_EXTRABOLD = "750"

LETTER_TIGHT = "-0.03em"
LETTER_SNUG = "-0.02em"
LETTER_NORMAL = "-0.01em"

# ── Shadows ──────────────────────────────────────────────────────────────────
SHADOW_SM = "0 4px 20px rgba(0,0,0,0.28)"
SHADOW_LG = "0 1.5rem 3.75rem rgba(0,0,0,0.6)"

# ── Transitions ──────────────────────────────────────────────────────────────
TRANS_DEFAULT = "all 0.15s ease"
TRANS_FAST = "all 0.12s ease"

# ── Blur ─────────────────────────────────────────────────────────────────────
BLUR_DEFAULT = "1rem"

# ── Card ─────────────────────────────────────────────────────────────────────
CARD_PREVIEW_HEIGHT = "12.5rem"
CARD_TEXT_CLAMP_STYLE = {
    "display": "-webkit-box",
    "-webkit-line-clamp": "3",
    "-webkit-box-orient": "vertical",
    "overflow": "hidden",
}


def clamp_lines(lines: int) -> dict[str, str]:
    return {
        "display": "-webkit-box",
        "-webkit-line-clamp": str(lines),
        "-webkit-box-orient": "vertical",
        "overflow": "hidden",
    }
