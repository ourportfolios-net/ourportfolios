import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def vnindex_mini_chart():
    """Create mini price chart for VNINDEX."""
    return rx.cond(
        HomeState.vnindex_chart_data,
        rx.vstack(
            rx.recharts.area_chart(
                rx.recharts.area(
                    data_key="normalized_close",
                    stroke=rx.color("purple", 9),
                    fill=rx.color("purple", 3),
                    stroke_width=2,
                ),
                rx.recharts.x_axis(data_key="name", hide=True),
                rx.recharts.y_axis(domain=[0, 1], hide=True),
                data=HomeState.vnindex_chart_data,
                width=80,
                height=40,
            ),
            spacing="0",
        ),
        rx.box(width="80px", height="40px"),
    )


def point_change_badge():
    """Badge showing point change with icon."""
    return rx.badge(
        rx.flex(
            rx.cond(
                HomeState.vnindex_is_positive,
                rx.icon(tag="arrow_up", size=12),
                rx.icon(tag="arrow_down", size=12),
            ),
            rx.text(HomeState.vnindex_change, size="1", weight="medium"),
            spacing="1",
            align="center",
        ),
        color_scheme=rx.cond(HomeState.vnindex_is_positive, "green", "red"),
        size="1",
        font_weight="700",
    )


def market_overview_section():
    """Create the market overview section with real VNINDEX data."""
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "VNIndex",
                            font_size="0.8em",
                            font_weight="400",
                            letter_spacing="0.1em",
                            color="rgba(255, 255, 255, 0.4)",
                        ),
                        rx.hstack(
                            rx.text(
                                HomeState.vnindex_value,
                                font_size="18px",
                                font_weight="700",
                            ),
                            point_change_badge(),
                            spacing="2",
                            align="center",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    vnindex_mini_chart(),
                    spacing="3",
                ),
                width="100%",
                align="center",
                margin_bottom="0.5rem",
            ),
            # Placeholder for heatmap
            rx.box(
                rx.text(
                    "Heatmap will be rendered here",
                    font_size="12px",
                    color="rgba(255, 255, 255, 0.3)",
                    font_style="italic",
                ),
                width="100%",
                height="500px",
                padding="1.5rem",
                border="1px dashed rgba(255, 255, 255, 0.1)",
                border_radius="12px",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="0.5rem",
            ),
            # View Full Market link
            rx.box(
                rx.link(
                    rx.hstack(
                        rx.text(
                            "VIEW FULL MARKET",
                            font_size="9px",
                            font_weight="700",
                            letter_spacing="0.1em",
                            color="rgba(255, 255, 255, 0.4)",
                            transition="all 0.3s ease",
                        ),
                        rx.icon(
                            "chevron-right",
                            size=12,
                            color="rgba(255, 255, 255, 0.4)",
                            transition="color 0.3s ease",
                        ),
                        spacing="1",
                    ),
                    href="/compare",
                    text_decoration="none",
                    _hover={
                        "& p": {
                            "color": "rgba(255, 255, 255, 0.55)",
                            "transform": "translateX(-4px)",
                        },
                        "& svg": {"color": "rgba(255, 255, 255, 0.55)"},
                    },
                ),
                display="flex",
                justify_content="flex-end",
                width="100%",
            ),
            spacing="0",
            width="100%",
        ),
        padding="0.75rem",
        width="100%",
        max_width="500px",
    )
