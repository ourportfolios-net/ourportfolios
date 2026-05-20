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
RADIUS_XL = "1.5rem"          # Landing hero cards
RADIUS_LG = "0.875rem"        # Primary cards, modals, section containers
RADIUS_MD = "0.75rem"         # Secondary surfaces, dropdowns, ticker cards
RADIUS_SM = "0.625rem"        # Form inputs, compact cards, icon boxes
RADIUS_XS = "0.5rem"          # Buttons, chips, small containers
RADIUS_2XS = "0.4375rem"      # Small badges, menu items
RADIUS_3XS = "0.375rem"       # Pills, tiny tags, mini badges
RADIUS_4XS = "0.3125rem"      # Period toggles, tiny elements
RADIUS_5XS = "0.25rem"        # Skeletons, progress bars
RADIUS_6XS = "0.125rem"       # Borders, hairline accents
RADIUS_FULL = "9999px"        # Avatars, circular elements

# ── Semantic radius aliases ──────────────────────────────────────────────────
RADIUS_CARD = RADIUS_LG
RADIUS_SURFACE = RADIUS_MD
RADIUS_INPUT = RADIUS_SM
RADIUS_BUTTON = RADIUS_XS
RADIUS_PILL = RADIUS_3XS

# ── Spacing / Padding ────────────────────────────────────────────────────────
SPACE_2XS = "0.375rem"        # Tight padding (dropdown items, tooltips)
SPACE_XS = "0.5rem"           # Compact padding
SPACE_SM = "0.75rem"          # Small padding (chart boxes, list rows)
SPACE_MD = "0.875rem"         # Medium padding (metric boxes)
SPACE_LG = "1rem"             # Default padding
SPACE_XL = "1.25rem"          # Comfortable padding (section containers)
SPACE_2XL = "1.5rem"          # Generous padding (cards, modals)
SPACE_3XL = "2rem"            # Large padding (modal panels)
SPACE_4XL = "3rem"            # Extra large (empty states, loading)

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
SHADOW_MODAL = "0 1.5625rem 3.75rem rgba(0, 0, 0, 0.6)"
SHADOW_DROPDOWN = "0 1rem 2.5rem rgba(0,0,0,0.55)"
SHADOW_NAVBAR = "0 10px 40px rgba(0,0,0,0.32)"
SHADOW_SEARCH = "0 1rem 3rem rgba(0, 0, 0, 0.45)"
SHADOW_CARD = "0 8px 28px rgba(0,0,0,0.6)"
SHADOW_GLOW_SM = "0 0 0.375rem rgba(124, 58, 237, 0.8)"
SHADOW_GLOW_MD = "0 0 0.5rem rgba(124, 58, 237, 0.6)"
SHADOW_FOCUS = "0 0 0 0.1875rem"

# ── Transitions ──────────────────────────────────────────────────────────────
TRANS_FAST = "all 0.12s ease"
TRANS_DEFAULT = "all 0.15s ease"
TRANS_SLOW = "all 0.2s ease"
TRANS_COLOR_FAST = "color 0.12s"
TRANS_COLOR = "color 0.2s"
TRANS_OPACITY = "opacity 0.15s ease"
TRANS_BG = "background 0.12s ease"

# ── Blur ─────────────────────────────────────────────────────────────────────
BLUR_SM = "0.75rem"
BLUR_MD = "0.875rem"
BLUR_LG = "1.25rem"
BLUR_XL = "1.5rem"
BLUR_NAVBAR = "18px"

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
