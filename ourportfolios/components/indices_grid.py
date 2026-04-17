"""Indices overview grid — renders one mini_chart_card per tracked index."""

import reflex as rx

from ..state.home_state import HomeState
from .mini_chart_card import mini_chart_card

# Must match the treemap height so the vertical scroll area is constrained
_TREEMAP_H = "38.75rem"


def _index_card(index: dict) -> rx.Component:
    return mini_chart_card(
        label=index["label"],
        value=index["value"],
        abs_change=index["abs_change"],
        pct_change=index["pct_change"],
        is_positive=index["is_positive"],
        chart_data=index["chart_data"],
    )


def _index_card_mobile(index: dict) -> rx.Component:
    """Fixed-width, non-shrinking wrapper for each card in the horizontal row."""
    return rx.box(
        mini_chart_card(
            label=index["label"],
            value=index["value"],
            abs_change=index["abs_change"],
            pct_change=index["pct_change"],
            is_positive=index["is_positive"],
            chart_data=index["chart_data"],
        ),
        # min_width="10.5rem",
        flex_shrink="0",
    )


def indices_grid() -> rx.Component:
    return rx.box(
        # ── Mobile: horizontal scroll area ────────────────────────────────
        rx.mobile_only(
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(HomeState.indices, _index_card_mobile),
                    spacing="3",
                    align="stretch",
                    wrap="nowrap",
                ),
                scrollbars="horizontal",
                type="scroll",
                width="100%",
            ),
        ),
        # ── Tablet + Desktop: vertical scroll area ─────────────────────────
        rx.tablet_and_desktop(
            rx.scroll_area(
                rx.grid(
                    rx.foreach(HomeState.indices, _index_card),
                    columns="1",
                    gap="0.75rem",
                    width="auto",
                ),
                scrollbars="vertical",
                type="hover",
                max_height=_TREEMAP_H,
            ),
        ),
    )
