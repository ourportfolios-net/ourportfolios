import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card


def vnindex_mini_chart():
    """Create small mini chart for VNINDEX."""
    return rx.cond(
        HomeState.vnindex_chart_data,
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="normalized_close",
                stroke=rx.color("accent", 9),
                fill=rx.color("accent", 3),
                stroke_width=2,
            ),
            rx.recharts.x_axis(data_key="name", hide=True),
            rx.recharts.y_axis(domain=[0, 1], hide=True),
            data=HomeState.vnindex_chart_data,
            width=100,
            height=50,
        ),
        rx.box(width="100px", height="50px"),
    )


def time_period_button(label: str, active: bool = False) -> rx.Component:
    """Time period toggle button."""
    return rx.box(
        rx.text(
            label,
            font_size="11px",
            font_weight="500",
            color="white" if active else "rgba(255, 255, 255, 0.4)",
        ),
        padding="0.25rem 0.625rem",
        border_radius="4px",
        background="rgba(255, 255, 255, 0.1)" if active else "transparent",
        cursor="pointer",
        _hover={"background": "rgba(255, 255, 255, 0.06)"} if not active else {},
        transition="background 0.15s ease",
    )


def sector_card(name: str, value: str, is_positive: bool = True) -> rx.Component:
    """Mini sector card with performance indicator."""
    return rx.box(
        rx.vstack(
            rx.text(
                name,
                font_size="10px",
                font_weight="500",
                letter_spacing="0.04em",
                color="var(--green-9)" if is_positive else "var(--red-9)",
            ),
            # Mini bar visualization
            rx.box(
                rx.box(
                    width="100%",
                    height="100%",
                    background=f"linear-gradient(180deg, {'rgba(16, 185, 129, 0.4)' if is_positive else 'rgba(239, 68, 68, 0.4)'} 0%, {'rgba(16, 185, 129, 0.15)' if is_positive else 'rgba(239, 68, 68, 0.15)'} 100%)",
                    border_radius="4px",
                ),
                width="100%",
                height="50px",
                border_radius="4px",
                overflow="hidden",
            ),
            rx.text(
                value,
                font_size="12px",
                font_weight="600",
                color="white",
            ),
            spacing="1",
            align="center",
            width="100%",
        ),
        padding="0.5rem",
        border_radius="8px",
        background="rgba(255, 255, 255, 0.03)",
        border="1px solid rgba(255, 255, 255, 0.06)",
        flex="1",
        min_width="70px",
    )


def sector_chip(name: str, value: str, is_positive: bool = True) -> rx.Component:
    """Compact sector chip for the row."""
    return rx.hstack(
        rx.text(
            name,
            font_size="10px",
            font_weight="500",
            color="rgba(255, 255, 255, 0.5)",
        ),
        rx.badge(
            value,
            color_scheme="green" if is_positive else "red",
            size="1",
            font_weight="600",
        ),
        spacing="2",
        align="center",
    )


def market_overview_section():
    """Market overview panel — VNIndex with mini chart and sector heatmap."""
    return glass_card(
        rx.vstack(
            # Header row: label + time period buttons
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="6px",
                        height="6px",
                        border_radius="50%",
                        background=rx.color("accent", 9),
                    ),
                    rx.text(
                        "MARKET OVERVIEW",
                        font_size="10px",
                        font_weight="500",
                        letter_spacing="0.08em",
                        color="rgba(255, 255, 255, 0.5)",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    time_period_button("1D", active=True),
                    time_period_button("1W"),
                    time_period_button("1M"),
                    time_period_button("1Y"),
                    spacing="1",
                    align="center",
                    padding="0.125rem",
                    border_radius="6px",
                    background="rgba(255, 255, 255, 0.03)",
                ),
                width="100%",
                align="center",
            ),
            # Main content row: VNIndex block on left, Heatmap on right
            rx.hstack(
                # Left: VNIndex block (label, value, badge, chart)
                rx.hstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                "VNIndex",
                                font_size="12px",
                                font_weight="500",
                                color="rgba(255, 255, 255, 0.5)",
                            ),
                            rx.text(
                                HomeState.vnindex_value,
                                font_size="20px",
                                font_weight="700",
                                color="white",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.badge(
                            HomeState.vnindex_change,
                            color_scheme=rx.cond(
                                HomeState.vnindex_is_positive, "green", "red"
                            ),
                            size="1",
                            font_weight="600",
                        ),
                        spacing="3",
                        align="end",
                    ),
                    vnindex_mini_chart(),
                    spacing="4",
                    align="center",
                ),
                # Right: Sector heatmap (main focus)
                rx.hstack(
                    sector_card("BANKS", "+2.4%", is_positive=True),
                    sector_card("REAL EST", "-0.8%", is_positive=False),
                    rx.vstack(
                        sector_chip("TECH", "+1.1%", is_positive=True),
                        sector_chip("RETAIL", "0.0%", is_positive=True),
                        spacing="2",
                    ),
                    spacing="3",
                    align="stretch",
                    flex="1",
                ),
                spacing="6",
                width="100%",
                align="center",
            ),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem",
        width="100%",
    )
