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
                    height="100%",
                    width="100%",
                    position="absolute",
                    top="0",
                    left="0",
                    z_index="1",
                ),
                href=f"/tickers/{HomeState.ticker_of_day_symbol}",
            ),
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.icon("star", size=14, color=rx.color("yellow", 9)),
                        rx.text(
                            "TICKER OF THE DAY",
                            font_size="10px",
                            font_weight="500",
                            letter_spacing="0.06em",
                            color=white(0.5),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text(
                            HomeState.ticker_of_day_symbol,
                            font_size="28px",
                            font_weight="700",
                            color="white",
                            line_height="1",
                        ),
                        rx.button(
                            rx.icon("shopping-cart", size=15),
                            size="1",
                            variant="outline",
                            on_click=CartState.add_item(HomeState.ticker_of_day_symbol),
                            position="relative",
                            z_index="10",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        HomeState.ticker_of_day_name,
                        font_size="12px",
                        font_weight="400",
                        color=white(0.5),
                        white_space="nowrap",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        max_width="200px",
                    ),
                    spacing="2",
                    align="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text(
                        HomeState.ticker_of_day_price,
                        font_size="20px",
                        font_weight="700",
                        color="white",
                    ),
                    rx.badge(
                        HomeState.ticker_of_day_change,
                        color_scheme="green",
                        size="1",
                        font_weight="600",
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
            position="relative",
            width="100%",
        ),
        padding="1rem",
        width="100%",
        cursor="pointer",
        transition="all 0.25s ease",
        _hover={"border_color": white(0.12)},
    )
