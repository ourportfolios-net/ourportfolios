"""Framework cards and sidebar components."""

import reflex as rx

from .state import FrameworkState


def category_filter_button(category):
    """Horizontal filter button for framework categories"""
    is_active = FrameworkState.active_category == category.value

    return rx.button(
        category.label,
        on_click=lambda: FrameworkState.set_active_category(category.value),
        variant="soft",
        color_scheme=rx.cond(is_active, "violet", "gray"),
        size="3",
        style={
            "border_radius": "2em",
            "padding": "0.75em 1.5em",
            "font_weight": "500",
            "transition": "all 0.2s ease",
            "cursor": "pointer",
        },
    )


def framework_card(framework):
    """Enhanced framework card with glassmorphic design"""

    # Risk level styling using model attributes
    risk_display = rx.cond(
        framework.complexity == "beginner-friendly",
        "Low",
        rx.cond(framework.complexity == "complex", "High", "Med"),
    )

    risk_color = rx.cond(
        framework.complexity == "beginner-friendly",
        "green",
        rx.cond(framework.complexity == "complex", "red", "amber"),
    )

    return rx.card(
        rx.vstack(
            # Icon and Badge
            rx.hstack(
                rx.box(
                    rx.icon("trending-up", size=24, color="#8B5CF6"),
                    style={
                        "background": "rgba(139, 92, 246, 0.15)",
                        "border_radius": "0.75em",
                        "padding": "0.75em",
                        "border": "1px solid rgba(139, 92, 246, 0.3)",
                    },
                ),
                rx.spacer(),
                rx.badge(
                    framework.scope,
                    color_scheme="violet",
                    variant="solid",
                    size="1",
                    style={
                        "font_weight": "600",
                        "letter_spacing": "0.05em",
                    },
                ),
                width="100%",
                align="center",
            ),
            # Title and Description
            rx.vstack(
                rx.heading(
                    framework.title,
                    size="5",
                    weight="bold",
                    style={
                        "background": "linear-gradient(135deg, #FFFFFF 0%, #A78BFA 100%)",
                        "background_clip": "text",
                        "color": "transparent",
                    },
                ),
                rx.text(
                    framework.description,
                    size="2",
                    color="gray",
                    style={
                        "line_height": "1.5",
                        "display": "-webkit-box",
                        "-webkit-line-clamp": "3",
                        "-webkit-box-orient": "vertical",
                        "overflow": "hidden",
                    },
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            rx.spacer(),
            # Metrics Row
            rx.hstack(
                rx.vstack(
                    rx.text("RISK LEVEL", size="1", color="gray", weight="medium"),
                    rx.text(risk_display, size="3", weight="bold", color=risk_color),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text("INDUSTRY", size="1", color="gray", weight="medium"),
                    rx.text(
                        framework.industry, size="3", weight="bold", color="violet"
                    ),
                    spacing="1",
                    align="start",
                ),
                width="100%",
                align="end",
            ),
            # Author and View Button
            rx.hstack(
                rx.text(
                    framework.author, size="1", color="gray", style={"opacity": "0.7"}
                ),
                rx.spacer(),
                rx.link(
                    rx.hstack(
                        rx.text("VIEW ASSETS", size="1", weight="bold"),
                        rx.icon("arrow-right", size=14),
                        spacing="1",
                        align="center",
                    ),
                    color="violet",
                ),
                width="100%",
                align="center",
            ),
            spacing="4",
            align="start",
            width="100%",
            height="100%",
            justify="between",
        ),
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        style={
            "background": "rgba(30, 30, 35, 0.8)",
            "backdrop_filter": "blur(20px)",
            "border": "1px solid rgba(139, 92, 246, 0.2)",
            "border_radius": "1.25em",
            "padding": "1.5em",
            "transition": "all 0.3s ease",
            "cursor": "pointer",
            "height": "280px",
        },
        _hover={
            "transform": "translateY(-0.5em)",
            "border_color": "rgba(139, 92, 246, 0.5)",
            "box_shadow": "0 1em 3em rgba(139, 92, 246, 0.2)",
        },
    )


def ticker_cart_sidebar():
    """Ticker cart sidebar matching the design"""
    return rx.card(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("shopping-cart", size=18, color="#8B5CF6"),
                rx.text("Ticker Cart", size="3", weight="bold"),
                rx.badge(
                    FrameworkState.ticker_cart_count,
                    color_scheme="violet",
                    variant="solid",
                    size="1",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            # Cart items
            rx.cond(
                FrameworkState.ticker_cart_count > 0,
                rx.vstack(
                    rx.foreach(
                        FrameworkState.ticker_cart,
                        lambda ticker: rx.hstack(
                            rx.text(ticker.symbol, size="3", weight="bold"),
                            rx.text(ticker.name, size="2", color="gray"),
                            rx.spacer(),
                            rx.icon_button(
                                rx.icon("x", size=14),
                                size="1",
                                variant="ghost",
                                on_click=lambda: FrameworkState.remove_from_cart(
                                    ticker.symbol
                                ),
                            ),
                            width="100%",
                            align="center",
                            padding="0.5em",
                            style={
                                "border_bottom": "1px solid rgba(139, 92, 246, 0.1)",
                            },
                        ),
                    ),
                    spacing="0",
                    width="100%",
                ),
                rx.center(
                    rx.text("No tickers selected", size="2", color="gray"),
                    padding="2em",
                ),
            ),
            rx.spacer(),
            # Compare button
            rx.button(
                "Compare Now",
                rx.icon("arrow-right", size=16),
                on_click=FrameworkState.navigate_to_compare,
                width="100%",
                size="3",
                color_scheme="violet",
                disabled=FrameworkState.ticker_cart_count == 0,
            ),
            spacing="3",
            width="100%",
            height="100%",
        ),
        style={
            "background": "rgba(30, 30, 35, 0.8)",
            "backdrop_filter": "blur(20px)",
            "border": "1px solid rgba(139, 92, 246, 0.2)",
            "border_radius": "1.25em",
            "padding": "1.5em",
            "width": "280px",
            "height": "fit-content",
            "position": "sticky",
            "top": "2em",
        },
    )
