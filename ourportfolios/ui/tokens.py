"""Centralized UI tokens for layout and scalable page composition."""

from __future__ import annotations

APP_BG = "#090909"
APP_SURFACE_BG = "#111111"
APP_PANEL_BG = "#0d0d0d"

PAGE_MAX_WIDTH = "90rem"
PAGE_EDGE_PADDING = "2rem"
PAGE_VERTICAL_PADDING = "2rem"
SECTION_GAP = "1.25rem"

HOME_CONTENT_WIDTH = "86vw"
HOME_CONTENT_MAX_WIDTH = PAGE_MAX_WIDTH
HOME_PAGE_HORIZONTAL_PADDING = PAGE_EDGE_PADDING
HOME_PAGE_VERTICAL_PADDING = PAGE_VERTICAL_PADDING

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
