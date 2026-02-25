import reflex as rx
from ...state.home_state import HomeState
from ...state.cart_state import CartState
from ...components.cards import glass_card
from ...styles import white


def ticker_of_the_day_card():
    return glass_card(
        rx.box(
            rx.link(
                rx.box(
                    position="absolute",
                    top="0",
                    left="0",
                    height="100%",
                    width="100%",
                    z_index="1",
                ),
                href=f"/analyze/{HomeState.ticker_of_day_symbol}",
            ),
            rx.vstack(
                # Eyebrow label — no icon
                rx.text(
                    "Ticker of the Day",
                    font_size="11px",
                    font_weight="500",
                    color=white(0.35),
                    letter_spacing="0.01em",
                ),
                # Main row
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                HomeState.ticker_of_day_symbol,
                                font_size="30px",
                                font_weight="800",
                                color="white",
                                letter_spacing="-0.02em",
                                line_height="1",
                            ),
                            rx.button(
                                rx.icon("shopping-cart", size=13),
                                size="1",
                                variant="outline",
                                on_click=CartState.add_item(
                                    HomeState.ticker_of_day_symbol
                                ),
                                position="relative",
                                z_index="10",
                                border_radius="7px",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(
                            HomeState.ticker_of_day_name,
                            font_size="11px",
                            color=white(0.35),
                            white_space="nowrap",
                            overflow="hidden",
                            text_overflow="ellipsis",
                            max_width="200px",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.text(
                            HomeState.ticker_of_day_price,
                            font_size="24px",
                            font_weight="800",
                            color="white",
                            letter_spacing="-0.02em",
                        ),
                        rx.badge(
                            HomeState.ticker_of_day_change,
                            color_scheme="green",
                            size="1",
                            font_weight="700",
                        ),
                        spacing="1",
                        align="end",
                    ),
                    width="100%",
                    align="center",
                    position="relative",
                    z_index="2",
                    pointer_events="none",
                    style={"& button": {"pointer-events": "auto"}},
                ),
                spacing="2",
                width="100%",
            ),
            position="relative",
            width="100%",
        ),
        padding="1.125rem 1.25rem",
        width="100%",
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={"border_color": white(0.12), "background": white(0.035)},
    )
