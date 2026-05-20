import reflex as rx

from ourportfolios.state.cart_state import CartState
from ourportfolios.ui.primitives import glass_box
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.tokens import RADIUS_4XS, RADIUS_BUTTON, TRANS_DEFAULT


def _cart_item_row(item: dict, index: int) -> rx.Component:
    return rx.hstack(
        rx.link(
            rx.text(
                item["name"],
                size="3",
                weight="bold",
                color="white",
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            href=f"/tickers/{item['name']}",
            underline="none",
            min_width="0",
            flex="1",
        ),
        rx.badge(
            item.get("industry", "Unknown"),
            variant="outline",
            color_scheme="gray",
            size="1",
            flex_shrink="0",
        ),
        rx.box(
            rx.icon("x", size=13, color=white(0.25)),
            on_click=lambda: CartState.remove_item(index),
            cursor="pointer",
            padding="0.25rem",
            border_radius=RADIUS_4XS,
            display="flex",
            align_items="center",
            justify_content="center",
            transition=TRANS_DEFAULT,
            _hover={"background": white(0.06), "color": "white"},
        ),
        align="center",
        width="100%",
        padding="0.75rem 0.875rem",
        border_radius=RADIUS_BUTTON,
        background=white(0.02),
        border=f"1px solid {white(0.05)}",
        transition=TRANS_DEFAULT,
        _hover={"background": white(0.035), "border_color": white(0.08)},
    )


def cart_card() -> rx.Component:
    return glass_box(
        rx.vstack(
            rx.text(
                "Comparison Cart",
                size="1",
                weight="medium",
                color=white(0.35),
            ),
            rx.cond(
                CartState.cart_items,
                rx.vstack(
                    rx.foreach(
                        CartState.cart_items,
                        _cart_item_row,
                    ),
                    spacing="2",
                    width="100%",
                    max_height="18.75rem",
                    overflow_y="auto",
                    scrollbar_width="thin",
                    scrollbar_color=f"{white(0.06)} transparent",
                ),
                rx.vstack(
                    rx.text("No tickers in cart", size="2", color=white(0.2)),
                    align="center",
                    width="100%",
                    padding_y="1rem",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        padding=rx.breakpoints(initial="0.875rem 1rem", md="1.125rem 1.25rem"),
        width="100%",
    )
