import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def portfolio_card_with_hover():
    """Create the portfolio card with unified performance visualization."""
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
                # Header row with title/description on left and icon on right
                rx.hstack(
                    rx.vstack(
                        rx.heading("Manage Portfolio", size="5", font_weight="700"),
                        rx.text(
                            "Track performance, view allocation and rebalance your current holdings.",
                            color="rgba(255, 255, 255, 0.5)",
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon("arrow-right-left", size=20, color="var(--green-9)"),
                        width="40px",
                        height="40px",
                        border_radius="10px",
                        background="rgba(16, 185, 129, 0.2)",
                        border="1px solid rgba(16, 185, 129, 0.3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        flex_shrink="0",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                # Spacer to push everything below to the bottom
                rx.box(flex="1"),
                # Combined section with total value and performance bars
                rx.vstack(
                    # Total value section
                    rx.vstack(
                        rx.box(
                            width="80px",
                            height="10px",
                            border_radius="4px",
                            background="rgba(255, 255, 255, 0.08)",
                        ),
                        rx.hstack(
                            rx.text(
                                HomeState.portfolio_value,
                                font_size="18px",
                                font_weight="700",
                                style={"transition": "all 1s ease"},
                            ),
                            rx.spacer(),
                            rx.badge(
                                HomeState.portfolio_change,
                                color_scheme="green",
                                size="1",
                                font_weight="700",
                                style={"transition": "all 1s ease"},
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                        margin_bottom="0.75rem",
                    ),
                    # Performance bars
                    rx.vstack(
                        # Bar 1 - extends to 70%
                        rx.hstack(
                            rx.box(
                                width="36px",
                                height="14px",
                                border_radius="4px",
                                background="rgba(255, 255, 255, 0.08)",
                            ),
                            rx.box(
                                rx.box(
                                    width=rx.cond(
                                        HomeState.is_portfolio_hovered, "70%", "50%"
                                    ),
                                    height="100%",
                                    background=rx.cond(
                                        HomeState.is_portfolio_hovered,
                                        "rgba(16, 185, 129, 0.5)",
                                        "rgba(255, 255, 255, 0.15)",
                                    ),
                                    border_radius="4px",
                                    transition="all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
                                ),
                                width="100%",
                                height="14px",
                                background="rgba(255, 255, 255, 0.05)",
                                border_radius="4px",
                                overflow="hidden",
                                flex="1",
                                max_width="calc(100% - 100px)",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        # Bar 2 - shrinks to 30%, darker green
                        rx.hstack(
                            rx.box(
                                width="36px",
                                height="14px",
                                border_radius="4px",
                                background="rgba(255, 255, 255, 0.08)",
                            ),
                            rx.box(
                                rx.box(
                                    width=rx.cond(
                                        HomeState.is_portfolio_hovered, "30%", "50%"
                                    ),
                                    height="100%",
                                    background=rx.cond(
                                        HomeState.is_portfolio_hovered,
                                        "rgba(16, 185, 129, 0.35)",
                                        "rgba(255, 255, 255, 0.15)",
                                    ),
                                    border_radius="4px",
                                    transition="all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
                                ),
                                width="100%",
                                height="14px",
                                background="rgba(255, 255, 255, 0.05)",
                                border_radius="4px",
                                overflow="hidden",
                                flex="1",
                                max_width="calc(100% - 100px)",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        # Bar 3 - shrinks to 30%, darker green
                        rx.hstack(
                            rx.box(
                                width="36px",
                                height="14px",
                                border_radius="4px",
                                background="rgba(255, 255, 255, 0.08)",
                            ),
                            rx.box(
                                rx.box(
                                    width=rx.cond(
                                        HomeState.is_portfolio_hovered, "30%", "50%"
                                    ),
                                    height="100%",
                                    background=rx.cond(
                                        HomeState.is_portfolio_hovered,
                                        "rgba(16, 185, 129, 0.35)",
                                        "rgba(255, 255, 255, 0.15)",
                                    ),
                                    border_radius="4px",
                                    transition="all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
                                ),
                                width="100%",
                                height="14px",
                                background="rgba(255, 255, 255, 0.05)",
                                border_radius="4px",
                                overflow="hidden",
                                flex="1",
                                max_width="calc(100% - 100px)",
                            ),
                            spacing="3",
                            align="center",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="0",
                    padding="0.75rem",
                    border_radius="10px",
                    background="rgba(255, 255, 255, 0.03)",
                    border="1px solid rgba(255, 255, 255, 0.05)",
                    width="100%",
                ),
                # Button
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
                width="100%",
                height="100%",
            ),
            padding="1rem",
            width="100%",
            height="420px",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        on_mouse_enter=HomeState.start_portfolio_hover,
        on_mouse_leave=HomeState.end_portfolio_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )
