"""Indices overview grid — renders one mini_chart_card per tracked index."""

import reflex as rx

from ..state.home_state import HomeState
from .mini_chart_card import mini_chart_card


def _index_card(index: dict) -> rx.Component:
    return mini_chart_card(
        label=index["label"],
        value=index["value"],
        abs_change=index["abs_change"],
        pct_change=index["pct_change"],
        is_positive=index["is_positive"],
        chart_data=index["chart_data"],
    )


def indices_grid() -> rx.Component:
    return rx.grid(
        rx.foreach(HomeState.indices, _index_card),
        columns="1",
        gap="0.75rem",
        width="auto",
    )
