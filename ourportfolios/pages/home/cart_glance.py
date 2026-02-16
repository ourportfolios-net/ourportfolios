"""Ticker cart glance panel for the home page."""

import reflex as rx
from ...state.cart_state import CartState
from ...components.cards import glass_card


def _cart_item_row(item: dict, index: int) -> rx.Component:
    """Single ticker row in the cart panel — matches drawer style."""
    return rx.card(
        rx.hstack(
            rx.hstack(
                rx.link(
                    rx.text(
                        item["name"],
                        size="4",
                        weight="medium",
                    ),
                    href=f"/analyze/{item['name']}",
                    underline="none",
                ),
                rx.badge(
                    item.get("industry", "Unknown"),
                    size="1",
                ),
                spacing="3",
                align_items="center",
            ),
            rx.button(
                rx.icon("list-minus", size=16),
                color_scheme="ruby",
                size="1",
                variant="soft",
                style={
                    "fontWeight": "medium",
                    "padding": "0.3em 0.7em",
                    "fontSize": "0.9em",
                },
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


def _cart_chip(item: dict, index: int) -> rx.Component:
    """Single ticker chip in the cart strip (legacy horizontal)."""
    return rx.hstack(
        rx.link(
            rx.text(
                item["name"],
                font_size="12px",
                font_weight="600",
                color="white",
            ),
            href=f"/analyze/{item['name']}",
            text_decoration="none",
        ),
        rx.text(
            "×",
            font_size="14px",
            color="rgba(255, 255, 255, 0.3)",
            cursor="pointer",
            _hover={"color": "rgba(255, 255, 255, 0.7)"},
            transition="color 0.15s ease",
            on_click=lambda: CartState.remove_item(index),
        ),
        spacing="2",
        align="center",
        padding="0.25rem 0.625rem",
        border_radius="6px",
        background="rgba(255, 255, 255, 0.06)",
        border="1px solid rgba(255, 255, 255, 0.08)",
        flex_shrink="0",
    )


def cart_glance_panel() -> rx.Component:
    """Vertical cart panel — shows saved tickers in a list."""
    return glass_card(
        rx.vstack(
            # Header: Just the text
            rx.text(
                "Comparison Cart",
                font_size="12px",
                font_weight="600",
                letter_spacing="0.02em",
                color="rgba(255, 255, 255, 0.6)",
            ),
            # Cart items list
            rx.cond(
                CartState.cart_items,
                rx.vstack(
                    rx.foreach(
                        CartState.cart_items,
                        lambda item, i: _cart_item_row(item, i),
                    ),
                    spacing="2",
                    width="100%",
                    max_height="400px",
                    overflow_y="auto",
                    style={
                        "scrollbarWidth": "thin",
                        "scrollbarColor": "rgba(255, 255, 255, 0.1) transparent",
                    },
                ),
                # Empty state
                rx.box(
                    rx.vstack(
                        rx.icon(
                            "package-open",
                            size=24,
                            color="rgba(255, 255, 255, 0.15)",
                        ),
                        rx.text(
                            "No tickers in cart",
                            font_size="12px",
                            color="rgba(255, 255, 255, 0.3)",
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


def cart_glance_strip() -> rx.Component:
    """Horizontal cart glance — shows saved tickers as chips (legacy)."""
    return rx.cond(
        CartState.cart_items,
        glass_card(
            rx.hstack(
                # Cart icon + label
                rx.hstack(
                    rx.icon(
                        "shopping-cart",
                        size=14,
                        color="rgba(255, 255, 255, 0.4)",
                    ),
                    rx.text(
                        "Your Cart",
                        font_size="11px",
                        font_weight="600",
                        letter_spacing="0.04em",
                        color="rgba(255, 255, 255, 0.4)",
                        white_space="nowrap",
                    ),
                    spacing="2",
                    align="center",
                    flex_shrink="0",
                ),
                # Separator
                rx.box(
                    width="1px",
                    height="20px",
                    background="rgba(255, 255, 255, 0.08)",
                    flex_shrink="0",
                ),
                # Scrollable chip row
                rx.hstack(
                    rx.foreach(
                        CartState.cart_items,
                        lambda item, i: _cart_chip(item, i),
                    ),
                    spacing="2",
                    align="center",
                    overflow_x="auto",
                    flex="1",
                    style={
                        "scrollbarWidth": "none",
                        "&::-webkit-scrollbar": {"display": "none"},
                    },
                ),
                # Open full cart
                rx.box(
                    rx.text(
                        "View All",
                        font_size="11px",
                        font_weight="600",
                        color="rgba(255, 255, 255, 0.35)",
                        white_space="nowrap",
                        cursor="pointer",
                        _hover={"color": "rgba(255, 255, 255, 0.6)"},
                        transition="color 0.15s ease",
                        on_click=CartState.toggle_cart,
                    ),
                    flex_shrink="0",
                ),
                spacing="4",
                width="100%",
                align="center",
            ),
            padding="0.625rem 1rem",
            width="100%",
        ),
        # Empty state — nothing rendered
        rx.fragment(),
    )
