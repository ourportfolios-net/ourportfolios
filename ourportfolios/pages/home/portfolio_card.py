import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def portfolio_card_with_hover():
    """Create the portfolio card with hover animation."""
    return rx.box(
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background="rgba(16, 185, 129, 0.1)",
            filter="blur(60px)",
            border_radius="9999px",
            transition="all 0.3s ease",
        ),
        glass_card(
            rx.vstack(
                rx.vstack(
                    rx.box(
                        rx.icon("wallet", size=20, color="var(--green-9)"),
                        width="40px",
                        height="40px",
                        border_radius="10px",
                        background="rgba(16, 185, 129, 0.2)",
                        border="1px solid rgba(16, 185, 129, 0.3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.heading("Manage Portfolio", size="5", font_weight="700"),
                    rx.text(
                        "Track your personal holdings, monitor risk exposure, and rebalance based on your strategy goals.",
                        color="rgba(255, 255, 255, 0.5)",
                        font_size="12px",
                        line_height="1.5",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "TOTAL VALUE",
                                    font_size="8px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                ),
                                rx.badge(
                                    HomeState.portfolio_change,
                                    color_scheme="green",
                                    size="1",
                                    font_weight="700",
                                    style={"transition": "all 1s ease"},
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.text(
                                HomeState.portfolio_value,
                                font_size="18px",
                                font_weight="700",
                                style={"transition": "all 1s ease"},
                            ),
                            spacing="1",
                            align="start",
                        ),
                        padding="0.75rem",
                        border_radius="10px",
                        background="rgba(255, 255, 255, 0.03)",
                        border="1px solid rgba(255, 255, 255, 0.05)",
                        width="100%",
                    ),
                    spacing="3",
                    align="start",
                    flex="1",
                ),
                rx.button(
                    "Open Portfolio Manager",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="outline",
                    on_click=HomeState.handle_portfolio,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                align="start",
                justify="between",
                height="100%",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            min_height="360px",
            transition="background 0.15s ease, border-color 0.15s ease",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        transition="all 0.3s ease",
        on_mouse_enter=HomeState.start_portfolio_hover,
        on_mouse_leave=HomeState.end_portfolio_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )
