import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def decision_hub_card(
    title: str,
    description: str,
    icon: str,
    color: str,
    button_text: str,
    button_variant: str,
    on_click,
    has_input: bool = False,
    has_progress: bool = False,
    has_portfolio_value: bool = False,
    has_framework_count: bool = False,
    has_comparison_count: bool = False,
    has_comparison_chart: bool = False,
    has_framework_list: bool = False,
):
    """Create a decision hub card."""
    blur_color = {
        "purple": "rgba(139, 92, 246, 0.1)",
        "blue": "rgba(59, 130, 246, 0.1)",
        "emerald": "rgba(16, 185, 129, 0.1)",
    }

    icon_bg = {
        "purple": "rgba(139, 92, 246, 0.2)",
        "blue": "rgba(59, 130, 246, 0.2)",
        "emerald": "rgba(16, 185, 129, 0.2)",
    }

    icon_border = {
        "purple": "rgba(139, 92, 246, 0.3)",
        "blue": "rgba(59, 130, 246, 0.3)",
        "emerald": "rgba(16, 185, 129, 0.3)",
    }

    icon_color = {
        "purple": "var(--accent-purple)",
        "blue": "var(--blue-9)",
        "emerald": "var(--green-9)",
    }

    return rx.box(
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background=blur_color.get(color, blur_color["purple"]),
            filter="blur(60px)",
            border_radius="9999px",
            transition="all 0.3s ease",
        ),
        glass_card(
            rx.vstack(
                # Header row
                rx.hstack(
                    rx.vstack(
                        rx.heading(title, size="5", font_weight="700"),
                        rx.text(
                            description,
                            color="rgba(255, 255, 255, 0.5)",
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon(
                            icon,
                            size=20,
                            color=icon_color.get(color, icon_color["purple"]),
                        ),
                        width="40px",
                        height="40px",
                        border_radius="10px",
                        background=icon_bg.get(color, icon_bg["purple"]),
                        border=f"1px solid {icon_border.get(color, icon_border['purple'])}",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        flex_shrink="0",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                # Spacer
                rx.box(flex="1"),
                # Visualization - with surrounding box matching portfolio
                rx.cond(
                    has_comparison_chart,
                    rx.box(
                        rx.vstack(
                            # Header row with sliding columns
                            rx.hstack(
                                # Empty space above ticker
                                rx.box(width="70px"),
                                # Sliding column 1
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="12px",
                                        border_radius="4px",
                                        background="rgba(255, 255, 255, 0.08)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                # Sliding column 2
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="12px",
                                        border_radius="4px",
                                        background="rgba(255, 255, 255, 0.08)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                spacing="3",
                                width="100%",
                                margin_bottom="0.5rem",
                            ),
                            # Row 1
                            rx.hstack(
                                # Ticker skeleton
                                rx.box(
                                    width="70px",
                                    height="24px",
                                    border_radius="6px",
                                    background="rgba(255, 255, 255, 0.08)",
                                ),
                                # Sliding value 1 - blue (best performer)
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="16px",
                                        border_radius="4px",
                                        background="rgba(59, 130, 246, 0.3)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                # Sliding value 2 - grey
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="16px",
                                        border_radius="4px",
                                        background="rgba(255, 255, 255, 0.1)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                                padding="0.6rem",
                                border_radius="8px",
                                background="rgba(255, 255, 255, 0.02)",
                                border="1px solid rgba(255, 255, 255, 0.04)",
                            ),
                            # Row 2
                            rx.hstack(
                                # Ticker skeleton
                                rx.box(
                                    width="70px",
                                    height="24px",
                                    border_radius="6px",
                                    background="rgba(255, 255, 255, 0.08)",
                                ),
                                # Sliding value 1 - grey
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="16px",
                                        border_radius="4px",
                                        background="rgba(255, 255, 255, 0.1)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                # Sliding value 2 - blue (best performer)
                                rx.box(
                                    rx.box(
                                        width="70px",
                                        height="16px",
                                        border_radius="4px",
                                        background="rgba(59, 130, 246, 0.3)",
                                    ),
                                    width=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "70px",
                                        "0px",
                                    ),
                                    opacity=rx.cond(
                                        HomeState.is_comparison_hovered,
                                        "1",
                                        "0",
                                    ),
                                    overflow="hidden",
                                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                                padding="0.6rem",
                                border_radius="8px",
                                background="rgba(255, 255, 255, 0.02)",
                                border="1px solid rgba(255, 255, 255, 0.04)",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        padding="0.75rem",
                        border_radius="10px",
                        background="rgba(255, 255, 255, 0.03)",
                        border="1px solid rgba(255, 255, 255, 0.05)",
                        width="100%",
                    ),
                ),
                # Button
                rx.button(
                    button_text,
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant=button_variant,
                    on_click=on_click,
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
        on_mouse_enter=HomeState.start_comparison_hover,
        on_mouse_leave=HomeState.end_comparison_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )
