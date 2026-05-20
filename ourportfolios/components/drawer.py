"""Cart drawer UI component."""

import reflex as rx

from ourportfolios.state import CartState
from ourportfolios.ui.tokens import (
    APP_SURFACE_BG,
    BLUR_MD,
    RADIUS_LG,
    SPACE_3XL,
    SPACE_LG,
    SPACE_SM,
    SPACE_XL,
)


def _cart_item(item: dict[str, str], i: int) -> rx.Component:
    """Single cart item card — shared by scroll and non-scroll layouts."""
    return rx.card(
        rx.hstack(
            rx.hstack(
                rx.link(
                    rx.text(item["name"], size="4", weight="medium"),
                    href=f"/tickers/{item['name']}",
                    underline="none",
                ),
                rx.badge(f"{item['industry']}", size="1"),
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
                on_click=lambda: CartState.remove_item(i),
            ),
            align_items="center",
            justify_content="space-between",
            width="100%",
        ),
        background_color=rx.color("accent", 2),
        padding="0.8em 1em",
        margin_bottom=SPACE_SM,
        width="100%",
    )


def _cart_items_list() -> rx.Component:
    """Cart item list, scrollable when there are many items."""
    items_vstack = rx.vstack(
        rx.foreach(CartState.cart_items, _cart_item),
        width="100%",
        spacing="1",
        padding="0 0.5em",
    )
    return rx.cond(
        CartState.should_scroll,
        rx.scroll_area(items_vstack, height="25rem", width="100%"),
        items_vstack,
    )


def _compare_from_cart_event() -> list:
    from ourportfolios.pages.tickers.state import TickersPageState  # noqa: PLC0415

    return [
        CartState.toggle_cart,
        TickersPageState.set_view_mode("compare"),
        rx.redirect("/tickers"),
    ]


def cart_drawer_content():
    return rx.drawer.content(
        rx.box(
            rx.vstack(
                rx.box(
                    rx.drawer.close(
                        rx.text(
                            rx.icon("x", size=20),
                            on_click=CartState.toggle_cart,
                            cursor="pointer",
                            user_select="none",
                            color=rx.color("accent", 10),
                            _hover={"color": rx.color("accent", 7)},
                        ),
                    ),
                    width="100%",
                    display="flex",
                    justify_content="flex-end",
                    margin_bottom=SPACE_LG,
                ),
                rx.heading("Tickers Cart", size="6", weight="medium"),
                rx.cond(
                    CartState.cart_items,
                    rx.box(
                        _cart_items_list(),
                        rx.button(
                            rx.text("Compare"),
                            size="3",
                            variant="solid",
                            on_click=_compare_from_cart_event,
                            position="fixed",
                            bottom=SPACE_XL,
                            right=SPACE_XL,
                            z_index="1000",
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
            padding=SPACE_3XL,
            border_radius=RADIUS_LG,
            backdrop_filter=f"blur({BLUR_MD})",
            background=APP_SURFACE_BG,
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
                position="fixed",
                bottom=SPACE_3XL,
                left=SPACE_3XL,
                z_index="1000",
            ),
        ),
        rx.drawer.overlay(on_click=CartState.toggle_cart),
        rx.drawer.portal(cart_drawer_content()),
        open=CartState.is_open,
        direction="left",
        handle_only=True,
    )
