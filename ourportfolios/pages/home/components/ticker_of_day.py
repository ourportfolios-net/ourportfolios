import reflex as rx
from ....state.home_state import HomeState
from ....state.cart_state import CartState
from ....components.cards import glass_card
from ....styles import white


def _skel(w: str = "100%", h: str = "0.75rem", r: str = "0.375rem") -> rx.Component:
    return rx.skeleton(rx.box(width=w, height=h), loading=True, border_radius=r)


def _ticker_skeleton() -> rx.Component:
    return glass_card(
        rx.vstack(
            _skel("6.25rem", "0.625rem"),
            rx.hstack(
                rx.hstack(
                    _skel("5rem", "2.5rem", "0.375rem"),
                    _skel("2rem", "2rem", "0.4375rem"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                _skel("4.5rem", "1.75rem", "0.375rem"),
                width="100%",
                align="end",
            ),
            rx.hstack(
                _skel("7.5rem", "0.625rem"),
                rx.spacer(),
                _skel("3.25rem", "1.125rem", "0.5rem"),
                width="100%",
                align="center",
            ),
            spacing="3",
            width="100%",
        ),
        padding=rx.breakpoints(initial="0.875rem 1rem", md="1rem 1.125rem"),
        width="100%",
    )


def ticker_of_the_day_card():
    return rx.cond(
        HomeState.ticker_of_day_symbol,
        _ticker_real(),
        _ticker_skeleton(),
    )


def _ticker_real():
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
                href=f"/tickers/{HomeState.ticker_of_day_symbol}",
            ),
            rx.vstack(
                rx.text(
                    rx.el.span("Ticker of the "),
                    rx.el.span(HomeState.ticker_period_label),
                    size="1",
                    weight="medium",
                    color=white(0.35),
                ),
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.text(
                                HomeState.ticker_of_day_symbol,
                                size=rx.breakpoints(initial="7", sm="8"),
                                weight="bold",
                                color="white",
                                letter_spacing="-0.03em",
                                line_height="1",
                            ),
                            rx.button(
                                rx.icon("plus", size=13),
                                size="2",
                                variant="outline",
                                on_click=CartState.add_item(
                                    HomeState.ticker_of_day_symbol
                                ),
                                cursor="pointer",
                                position="relative",
                                z_index="10",
                                border_radius="0.4375rem",
                            ),
                            spacing="2",
                            align="end",
                        ),
                        rx.spacer(),
                        rx.text(
                            HomeState.ticker_of_day_price,
                            size=rx.breakpoints(initial="5", sm="6"),
                            weight="bold",
                            color="white",
                            letter_spacing="-0.02em",
                            line_height="1",
                        ),
                        width="100%",
                        align="end",
                        position="relative",
                        z_index="2",
                        pointer_events="none",
                        style={"& button": {"pointer-events": "auto"}},
                    ),
                    rx.hstack(
                        rx.text(
                            HomeState.ticker_of_day_name,
                            size="1",
                            color=white(0.28),
                            white_space="nowrap",
                            overflow="hidden",
                            text_overflow="ellipsis",
                            min_width="0",
                        ),
                        rx.spacer(),
                        rx.badge(
                            HomeState.ticker_of_day_change,
                            color_scheme="green",
                            size="1",
                            weight="bold",
                            flex_shrink="0",
                        ),
                        width="100%",
                        align="center",
                    ),
                    spacing="1",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            position="relative",
            width="100%",
        ),
        padding=rx.breakpoints(initial="0.875rem 1rem", md="1rem 1.125rem"),
        width="100%",
        cursor="pointer",
    )
