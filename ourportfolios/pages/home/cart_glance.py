"""Ticker cart glance panel for the home page."""

import reflex as rx
from ...state.cart_state import CartState
from ...components.cards import glass_card
from ...styles import white


def _cart_item_row(item: dict, index: int) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.hstack(
                rx.link(
                    rx.text(item["name"], size="4", weight="medium"),
                    href=f"/tickers/{item['name']}",
                    underline="none",
                ),
                rx.badge(item.get("industry", "Unknown"), size="1"),
                spacing="3",
                align_items="center",
            ),
            rx.button(
                rx.icon("list-minus", size=16),
                color_scheme="ruby",
                size="1",
                variant="soft",
                font_weight="medium",
                padding="0.3em 0.7em",
                font_size="0.9em",
                on_click=lambda: CartState.remove_item(index),
            ),
            align_items="center",
            justify_content="space-between",
            width="100%",
        ),
        background_color=rx.color("accent", 2),
        padding="0.8em 1em",
        width="100%",
    )


def cart_glance_panel() -> rx.Component:
    return glass_card(
        rx.vstack(
            rx.text(
                "Comparison Cart",
                font_size="0.75rem",
                font_weight="600",
                letter_spacing="0.02em",
                color=white(0.6),
            ),
            rx.cond(
                CartState.cart_items,
                rx.vstack(
                    rx.foreach(
                        CartState.cart_items, lambda item, i: _cart_item_row(item, i)
                    ),
                    spacing="2",
                    width="100%",
                    max_height="25rem",
                    overflow_y="auto",
                    scrollbar_width="thin",
                    scrollbar_color=f"{white(0.1)} transparent",
                ),
                rx.box(
                    rx.vstack(
                        rx.icon("package-open", size=24, color=white(0.15)),
                        rx.text(
                            "No tickers in cart", font_size="0.75rem", color=white(0.3)
                        ),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    padding_y="2rem",
                    display="flex",
                    justify_content="center",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        padding="1rem",
        width="100%",
    )
