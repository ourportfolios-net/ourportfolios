import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def ticker_of_the_day_card():
    """Create the ticker of the day card showing the most actively traded ticker with highest gain."""
    return rx.box(
        rx.vstack(
            rx.text(
                "TICKER OF THE DAY",
                font_size="9px",
                letter_spacing="0.08em",
                color="rgba(255, 255, 255, 0.35)",
                margin_bottom="0.5rem",
                padding_left="1rem",
            ),
            rx.box(
                rx.box(
                    # Yellow glow effect
                    rx.box(
                        position="absolute",
                        right="-2rem",
                        top="-2rem",
                        width="120px",
                        height="120px",
                        background="rgba(234, 179, 8, 0.15)",
                        filter="blur(40px)",
                        border_radius="9999px",
                        transition="all 0.5s ease",
                        z_index="0",
                    ),
                    glass_card(
                        rx.vstack(
                            # Top row - Symbol and badge
                            rx.hstack(
                                rx.text(
                                    HomeState.ticker_of_day_symbol,
                                    font_size="36px",
                                    font_weight="700",
                                    letter_spacing="-0.02em",
                                ),
                                rx.spacer(),
                                rx.badge(
                                    rx.flex(
                                        rx.icon(tag="arrow_up", size=10),
                                        rx.text(
                                            HomeState.ticker_of_day_change,
                                            size="1",
                                            weight="medium",
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    color_scheme="green",
                                    size="2",
                                    font_weight="600",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                            ),
                            # Bottom row - Company info
                            rx.hstack(
                                rx.text(
                                    HomeState.ticker_of_day_name,
                                    font_size="11px",
                                    font_weight="500",
                                    color="rgba(255, 255, 255, 0.75)",
                                ),
                                rx.text(
                                    "•",
                                    font_size="11px",
                                    color="rgba(255, 255, 255, 0.25)",
                                ),
                                rx.text(
                                    HomeState.ticker_of_day_industry,
                                    font_size="11px",
                                    font_weight="400",
                                    color="rgba(255, 255, 255, 0.35)",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        padding="0.875rem 1.25rem",
                        width="100%",
                        cursor="pointer",
                        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                        on_click=HomeState.navigate_to_ticker_of_day,
                        position="relative",
                        z_index="1",
                        _hover={
                            "background": "rgba(255, 255, 255, 0.06)",
                        },
                    ),
                    position="relative",
                    overflow="hidden",
                    width="100%",
                    transition="transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    _hover={
                        "transform": "translateX(8px)",
                        "& > :first-child": {
                            "background": "rgba(234, 179, 8, 0.22)",
                            "filter": "blur(45px)",
                        },
                    },
                ),
                width="100%",
                padding_left="1rem",
                padding_right="1rem",
                overflow="visible",
            ),
            spacing="0",
            width="100%",
        ),
        height="100%",
        position="relative",
    )
