import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def skeleton_box(width: str, height: str = "12px") -> rx.Component:
    """Create a static skeleton placeholder box."""
    return rx.box(
        width=width,
        height=height,
        border_radius="4px",
        background="rgba(255, 255, 255, 0.08)",
    )


def framework_skeleton_card(icon_name: str, index: int) -> rx.Component:
    """Create a skeleton framework card."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=18, color="rgba(255, 255, 255, 0.3)"),
                width="36px",
                height="36px",
                border_radius="12px",
                background="rgba(255, 255, 255, 0.05)",
                border="1px solid rgba(255, 255, 255, 0.08)",
                display="flex",
                align_items="center",
                justify_content="center",
                opacity=rx.cond(HomeState.framework_hover_index == index, "0", "1"),
                transition="opacity 0.3s ease",
            ),
            rx.vstack(
                skeleton_box("80%", "13px"),
                rx.vstack(
                    skeleton_box("95%", "8px"),
                    skeleton_box("70%", "8px"),
                    spacing="1",
                    width="100%",
                    margin_top="4px",
                ),
                spacing="1",
                align="start",
                flex="1",
                overflow="hidden",
                opacity=rx.cond(HomeState.framework_hover_index == index, "0", "1"),
                transition="opacity 0.3s ease",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.75rem",
        border_radius="10px",
        background="rgba(255, 255, 255, 0.03)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        width="100%",
        height="72px",
    )


def framework_glass_block(icon_name: str, title: str, description: str) -> rx.Component:
    """Glass block content for framework cards."""
    return rx.hstack(
        rx.box(
            rx.icon(icon_name, size=18, color="var(--indigo-9)"),
            width="36px",
            height="36px",
            border_radius="12px",
            background="rgba(99, 102, 241, 0.15)",
            border="1px solid rgba(99, 102, 241, 0.3)",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(
                title,
                font_size="13px",
                font_weight="700",
                color="white",
                line_height="1",
            ),
            rx.text(
                description,
                font_size="11px",
                color="rgba(255, 255, 255, 0.6)",
                line_height="1.4",
                margin_top="4px",
            ),
            spacing="1",
            align="start",
            flex="1",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.75rem",
    )


def select_framework_card() -> rx.Component:
    """Create the Select Framework card with glass spotlight effect."""
    card_height = "72px"

    return rx.box(
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background="rgba(139, 92, 246, 0.1)",
            filter="blur(60px)",
            border_radius="9999px",
            transition="all 0.3s ease",
        ),
        glass_card(
            rx.vstack(
                # Header row
                rx.hstack(
                    rx.vstack(
                        rx.heading("Select Framework", size="5", font_weight="700"),
                        rx.text(
                            "Choose an investment framework or screening methodology to guide your portfolio construction strategy.",
                            color="rgba(255, 255, 255, 0.5)",
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon("layers", size=20, color="var(--accent-purple)"),
                        width="40px",
                        height="40px",
                        border_radius="12px",
                        background="rgba(139, 92, 246, 0.2)",
                        border="1px solid rgba(139, 92, 246, 0.3)",
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
                # Framework visualization - with surrounding box matching portfolio
                rx.box(
                    rx.vstack(
                        # Total value section matching portfolio
                        rx.vstack(
                            rx.box(
                                width="80px",
                                height="10px",
                                border_radius="4px",
                                background="rgba(255, 255, 255, 0.08)",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                            margin_bottom="0.75rem",
                        ),
                        rx.box(
                            rx.vstack(
                                framework_skeleton_card(icon_name="shield", index=0),
                                framework_skeleton_card(icon_name="zap", index=1),
                                spacing="2",
                                align="start",
                                width="100%",
                            ),
                            rx.box(
                                rx.box(
                                    rx.box(
                                        framework_glass_block(
                                            icon_name="shield",
                                            title="Value Investing",
                                            description="Focuses on undervalued assets with strong fundamentals.",
                                        ),
                                        position="absolute",
                                        top="0",
                                        left="0",
                                        right="0",
                                        height=card_height,
                                    ),
                                    rx.box(
                                        framework_glass_block(
                                            icon_name="zap",
                                            title="Growth Strategy",
                                            description="Targets high-growth companies with expanding market share.",
                                        ),
                                        position="absolute",
                                        top=f"calc({card_height} + 8px)",
                                        left="0",
                                        right="0",
                                        height=card_height,
                                    ),
                                    position="absolute",
                                    top=rx.cond(
                                        HomeState.framework_hover_index == 0,
                                        "0",
                                        f"calc(-{card_height} - 8px)",
                                    ),
                                    left="0",
                                    right="0",
                                    height=f"calc({card_height} * 2 + 8px)",
                                    transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                position="absolute",
                                top=rx.cond(
                                    HomeState.framework_hover_index == 0,
                                    "0",
                                    f"calc({card_height} + 8px)",
                                ),
                                left="0",
                                right="0",
                                height=card_height,
                                background="linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.04) 100%)",
                                backdrop_filter="blur(8px)",
                                border_radius="10px",
                                border="1.5px solid rgba(99, 102, 241, 0.4)",
                                box_shadow="0 4px 20px rgba(99, 102, 241, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.1)",
                                overflow="hidden",
                                transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                pointer_events="none",
                            ),
                            position="relative",
                            width="100%",
                            height=f"calc({card_height} * 2 + 8px)",
                        ),
                        spacing="0",
                        align="start",
                        width="100%",
                    ),
                    padding="0.75rem",
                    border_radius="10px",
                    background="rgba(255, 255, 255, 0.03)",
                    border="1px solid rgba(255, 255, 255, 0.05)",
                    width="100%",
                ),
                # Button
                rx.button(
                    "Browse Frameworks",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="solid",
                    on_click=rx.redirect("/recommend"),
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
        on_mouse_enter=HomeState.start_framework_hover,
        on_mouse_leave=HomeState.stop_framework_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )
