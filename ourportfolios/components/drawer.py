"""Cart drawer UI component."""

import reflex as rx
from ..state import CartState


def cart_drawer_content():
    return rx.drawer.content(
        rx.box(
            rx.vstack(
                rx.box(
                    rx.drawer.close(
                        rx.text(
                            rx.icon("x", size=20),
                            on_click=CartState.toggle_cart,
                            style={
                                "marginLeft": "auto",
                                "cursor": "pointer",
                                "userSelect": "none",
                                "color": rx.color("accent", 10),
                                "_hover": {
                                    "color": rx.color("accent", 7),
                                },
                            },
                        )
                    ),
                    width="100%",
                    display="flex",
                    justify_content="flex-end",
                    margin_bottom="1em",
                ),
                rx.heading(
                    "Tickers Cart",
                    size="6",
                    weight="medium",
                ),
                rx.cond(
                    CartState.cart_items,
                    rx.box(
                        rx.cond(
                            CartState.should_scroll,
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        CartState.cart_items,
                                        lambda item, i: rx.card(
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
                                                        f"{item['industry']}",
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
                                                    on_click=lambda: CartState.remove_item(
                                                        i
                                                    ),
                                                ),
                                                align_items="center",
                                                justify_content="space-between",
                                                width="100%",
                                            ),
                                            background_color=rx.color("accent", 2),
                                            padding="0.8em 1em",
                                            margin_bottom="0.7em",
                                            width="100%",  # Changed from "92%" to "100%"
                                        ),
                                    ),
                                    width="100%",
                                    spacing="1",
                                    padding="0 0.5em",  # Add padding to the container instead
                                ),
                                height="400px",
                                width="100%",  # Ensure scroll area takes full width
                            ),
                            rx.vstack(
                                rx.foreach(
                                    CartState.cart_items,
                                    lambda item, i: rx.card(
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
                                                    f"{item['industry']}",
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
                                                on_click=lambda: CartState.remove_item(
                                                    i
                                                ),
                                            ),
                                            align_items="center",
                                            justify_content="space-between",
                                            width="100%",
                                        ),
                                        background_color=rx.color("accent", 2),
                                        padding="0.8em 1em",
                                        margin_bottom="0.7em",
                                        width="100%",  # Keep consistent with scroll area version
                                    ),
                                ),
                                width="100%",
                                spacing="1",
                                padding="0 0.5em",  # Add same padding for consistency
                            ),
                        ),
                        # Bottom right button - only shows when cart has items
                        rx.link(
                            rx.button(
                                rx.text("Compare"),
                                size="3",
                                variant="solid",
                                on_click=CartState.toggle_cart,
                                style={
                                    "position": "fixed",
                                    "bottom": "20px",
                                    "right": "20px",
                                    "zIndex": "1000",
                                },
                            ),
                            href="/analyze/compare",
                        ),
                        position="relative",
                        width="100%",
                    ),
                    rx.text("Your cart is empty."),
                ),
                spacing="5",
                align_items="start",
            ),
            width="100%",
            padding="2em",
            border_radius="1em",
            style={
                "backdropFilter": "blur(14px)",
                "background": "rgba(20, 20, 20, 0.7)",
            },
        ),
        width="28em",
        padding="1.5em 1em 1em 1em",
        background_color="transparent",
    )


def drawer_button():
    return rx.drawer.root(
        rx.drawer.trigger(
            rx.button(
                rx.icon("shopping-cart", size=16),
                on_click=CartState.toggle_cart,
                style={
                    "position": "fixed",
                    "bottom": "2em",
                    "left": "2em",
                    "z_index": 1000,
                },
            )
        ),
        rx.drawer.overlay(on_click=CartState.toggle_cart),
        rx.drawer.portal(cart_drawer_content()),
        open=CartState.is_open,
        direction="left",
        handle_only=True,
    )
