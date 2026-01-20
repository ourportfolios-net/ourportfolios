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
                # Visualization
                rx.cond(
                    has_comparison_chart,
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(
                                    rx.hstack(
                                        rx.icon("trending-up", size=12),
                                        rx.text(
                                            "VNM", font_size="11px", font_weight="700"
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    color_scheme="cyan",
                                    variant="soft",
                                    size="2",
                                    border_radius="12px",
                                    padding="0.5rem 0.75rem",
                                ),
                                rx.badge(
                                    rx.hstack(
                                        rx.icon("trending-up", size=12),
                                        rx.text(
                                            "VCB", font_size="11px", font_weight="700"
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    color_scheme="purple",
                                    variant="soft",
                                    size="2",
                                    border_radius="12px",
                                    padding="0.5rem 0.75rem",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.box(
                                rx.recharts.area_chart(
                                    rx.recharts.area(
                                        data_key="AAPL",
                                        stroke=rx.color("cyan", 9),
                                        fill=rx.color("cyan", 3),
                                        stroke_width=2,
                                        type_="monotone",
                                    ),
                                    rx.recharts.area(
                                        data_key="MSFT",
                                        stroke=rx.color("violet", 9),
                                        fill=rx.color("violet", 3),
                                        stroke_width=2,
                                        type_="monotone",
                                    ),
                                    rx.recharts.x_axis(data_key="period", hide=True),
                                    rx.recharts.y_axis(hide=True),
                                    data=HomeState.comparison_preview_data,
                                    width="100%",
                                    height=100,
                                    margin={
                                        "top": 5,
                                        "right": 5,
                                        "left": 5,
                                        "bottom": 5,
                                    },
                                ),
                                width="100%",
                                height="100px",
                                position="relative",
                            ),
                            spacing="3",
                            align="start",
                            width="100%",
                        ),
                        padding="1rem",
                        border_radius="12px",
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
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )
