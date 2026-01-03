"""Stock selection page with filtering and industry browsing."""

import reflex as rx

from ...components.navbar import navbar
from ...components.drawer import drawer_button
from ...components.page_roller import card_roller, card_link
from ...components.ticker_board import ticker_board

from .state import State
from .controls import ticker_filter


def page_selection():
    return rx.box(
        card_roller(
            card_link(
                rx.hstack(
                    rx.icon("chevron_left", size=32),
                    rx.vstack(
                        rx.heading("Recommend", weight="regular", size="5"),
                        rx.text("caijdo", size="1"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    align="center",
                    justify="center",
                ),
                href="/recommend",
            ),
            card_link(
                rx.vstack(
                    rx.heading("Select", weight="regular", size="7"),
                    rx.text("caijdo", size="3"),
                    align="center",
                    justify="center",
                    height="100%",
                    spacing="1",
                ),
                href="/select",
            ),
            card_link(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Analyze", weight="regular", size="5"),
                        rx.text("caijdo", size="1"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    rx.icon("chevron_right", size=32),
                    align="center",
                    justify="center",
                ),
                href="/analyze",
            ),
        ),
        width="100%",
        display="flex",
        justify_content="center",
        align_items="center",
        margin="0",
        padding="0",
    )


def industry_roller():
    return rx.box(
        rx.box(
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(
                        State.industry_filter.items(),
                        lambda item: rx.card(
                            rx.link(
                                rx.inset(
                                    rx.image(
                                        src="/placeholder-industry.png",
                                        width="40px",
                                        height="40px",
                                        style={"marginBottom": "0.5em"},
                                    ),
                                    item[0],
                                    style={
                                        "height": "120px",
                                        "minWidth": "200px",
                                        "padding": "1em",
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "alignItems": "flex-start",
                                        "whiteSpace": "normal",
                                        "overflow": "visible",
                                    },
                                    side="right",
                                ),
                                href=f"/select/{item[0].lower()}",
                                underline="none",
                            )
                        ),
                    ),
                    spacing="2",
                    height="100%",
                    align_items="flex-start",
                ),
                style={"height": 140, "width": 1000, "position": "relative"},
                scrollbars="horizontal",
                type="scroll",
            ),
            rx.cond(
                State.show_arrow,
                rx.box(
                    rx.icon("chevron_right", size=36, color="white"),
                    style={
                        "position": "absolute",
                        "top": "46%",
                        "right": "0",
                        "transform": "translateY(-50%)",
                        "height": "100%",
                        "width": "60px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "pointerEvents": "none",
                        "zIndex": 2,
                    },
                ),
            ),
            style={"position": "relative"},
        ),
    )


def card_with_scrollable_area():
    return rx.card(
        rx.segmented_control.root(
            rx.segmented_control.item("Markets", value="markets"),
            rx.segmented_control.item("Coin", value="coin"),
            rx.segmented_control.item("qqjdos", value="test"),
            on_change=State.set_control,
            value=State.control,
            size="1",
            style={"height": "2em"},
        ),
        style={
            "boxShadow": "0 2px 8px rgba(0,0,0,0.1)",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
        },
    )


@rx.page(
    route="/select",
    on_load=[
        State.on_mount,
        State.get_all_industries,
        State.get_all_exchanges,
        State.get_fundamentals_default_value,
        State.get_technicals_default_value,
        State.set_search_query(""),
    ],
)
def index():
    return rx.vstack(
        navbar(),
        page_selection(),
        rx.hstack(
            rx.vstack(
                rx.text("asdjfkhsdjf"),
                industry_roller(),
                # Filters
                ticker_filter(),
                # Tickers info
                ticker_board(),
                spacing="1",
                width="62em",
            ),
            card_with_scrollable_area(),
            width="100%",
            justify="center",
            spacing="6",
            padding="2em",
            padding_top="5em",
        ),
        drawer_button(),
    )
