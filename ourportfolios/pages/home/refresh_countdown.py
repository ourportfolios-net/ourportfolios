"""Refresh countdown rendered directly from HomeState."""

import reflex as rx
from ...state.home_state import HomeState
from ...styles import white

_CIRC = 54.85


def refresh_countdown_ring() -> rx.Component:
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.box(
                rx.el.svg(
                    rx.el.rect(
                        x="1.5",
                        y="1.5",
                        width="15",
                        height="15",
                        rx="3",
                        fill="none",
                        stroke=white(0.12),
                        stroke_width="1.6",
                    ),
                    rx.el.rect(
                        x="1.5",
                        y="1.5",
                        width="15",
                        height="15",
                        rx="3",
                        fill="none",
                        stroke=white(0.65),
                        stroke_width="1.6",
                        stroke_dasharray=str(_CIRC),
                        stroke_dashoffset=HomeState.refresh_countdown_ring_offset,
                        stroke_linecap="round",
                        style={"transition": "stroke-dashoffset 0.35s linear"},
                    ),
                    view_box="0 0 18 18",
                    width="14px",
                    height="14px",
                    style={"flex-shrink": "0", "overflow": "visible"},
                ),
                display="flex",
                align_items="center",
                justify_content="center",
                cursor="default",
                opacity="0.45",
                transition="opacity 0.2s ease",
                _hover={"opacity": "0.9"},
            ),
        ),
        rx.hover_card.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("timer", size=10, color=white(0.3)),
                    rx.text("Next refresh in", size="1", color=white(0.3)),
                    spacing="1",
                    align="center",
                ),
                rx.text(
                    HomeState.refresh_countdown_label,
                    size="5",
                    weight="bold",
                    color="white",
                    letter_spacing="-0.025em",
                    line_height="1",
                ),
                rx.box(width="100%", height="1px", background=white(0.06)),
                rx.text(
                    "Data is cached & refreshed every 30 min due to API rate limits.",
                    size="1",
                    color=white(0.25),
                    line_height="1.65",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            background="rgba(14, 14, 16, 0.98)",
            border=f"1px solid {white(0.07)}",
            border_radius="0.625rem",
            padding="0.75rem 0.875rem",
            box_shadow="0 8px 28px rgba(0,0,0,0.6)",
            max_width="195px",
            z_index="200",
        ),
        open_delay=50,
        close_delay=80,
    )
