"""Indices overview grid — renders one mini_chart_card per tracked index."""

import reflex as rx

from ourportfolios.components.mini_chart_card import (
    MiniChartCardProps,
    mini_chart_card,
)
from ourportfolios.state.home_state import HomeState
from ourportfolios.ui.tokens import RADIUS_SM

# Must match the treemap height so the vertical scroll area is constrained
_TREEMAP_H = "38.75rem"
_SKELETON_CARD_COUNT = 7


def _index_card(index: dict) -> rx.Component:
    return mini_chart_card(
        MiniChartCardProps(
            label=index["label"],
            value=index["value"],
            abs_change=index["abs_change"],
            pct_change=index["pct_change"],
            is_positive=index["is_positive"],
            chart_data=index["chart_data"],
        ),
    )


def _index_card_mobile(index: dict) -> rx.Component:
    """Fixed-width, non-shrinking wrapper for each card in the horizontal row."""
    return rx.box(
        mini_chart_card(
            MiniChartCardProps(
                label=index["label"],
                value=index["value"],
                abs_change=index["abs_change"],
                pct_change=index["pct_change"],
                is_positive=index["is_positive"],
                chart_data=index["chart_data"],
            ),
        ),
        min_width="10.5rem",
        flex_shrink="0",
    )


def _index_card_skeleton() -> rx.Component:
    return mini_chart_card(
        MiniChartCardProps(
            label="",
            value="",
            abs_change="",
            pct_change="",
            is_positive=True,
            chart_data=[],
        ),
    )


def indices_grid() -> rx.Component:
    return rx.box(
        # ── Mobile: horizontal scroll area ────────────────────────────────
        rx.mobile_only(
            rx.box(
                rx.cond(
                    HomeState.indices != [],
                    rx.hstack(
                        rx.foreach(HomeState.indices, _index_card_mobile),
                        spacing="3",
                        align="stretch",
                        wrap="nowrap",
                        width="max-content",
                    ),
                    rx.hstack(
                        *[
                            rx.box(
                                _index_card_skeleton(),
                                min_width="10.5rem",
                                flex_shrink="0",
                            )
                            for _ in range(_SKELETON_CARD_COUNT)
                        ],
                        spacing="3",
                        align="stretch",
                        wrap="nowrap",
                        width="max-content",
                    ),
                ),
                width="100%",
                max_width="100%",
                min_width="1px",
                overflow_x="auto",
                overflow_y="hidden",
                padding_bottom=RADIUS_SM,
            ),
            width="100%",
        ),
        # ── Tablet + Desktop: vertical scroll area ─────────────────────────
        rx.tablet_and_desktop(
            rx.scroll_area(
                rx.cond(
                    HomeState.indices != [],
                    rx.grid(
                        rx.foreach(HomeState.indices, _index_card),
                        columns="1",
                        gap="0.75rem",
                        width="auto",
                    ),
                    rx.grid(
                        *[_index_card_skeleton() for _ in range(_SKELETON_CARD_COUNT)],
                        columns="1",
                        gap="0.75rem",
                        width="auto",
                    ),
                ),
                scrollbars="vertical",
                type="hover",
                height=_TREEMAP_H,
                max_height=_TREEMAP_H,
            ),
        ),
        width="100%",
        min_width="0",
    )
