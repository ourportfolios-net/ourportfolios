"""Framework cards and sidebar components."""

import reflex as rx

from .state import FrameworkState


def category_filter_button(category):
    """Category filter button"""
    is_active = FrameworkState.active_category == category.value

    return rx.button(
        category.label,
        on_click=lambda: FrameworkState.set_active_category(category.value),
        variant="soft",
        color_scheme=rx.cond(is_active, "violet", "gray"),
        size="3",
    )


def framework_card(framework):
    """Framework card matching homepage design language"""

    return rx.card(
        rx.vstack(
            # Icon and scope badge
            rx.hstack(
                rx.icon("trending-up", size=20),
                rx.spacer(),
                rx.badge(
                    framework.scope,
                    color_scheme="violet",
                    variant="soft",
                ),
                width="100%",
                align="center",
            ),
            # Title
            rx.heading(framework.title, size="5", weight="bold"),
            # Description
            rx.text(
                framework.description,
                size="2",
                color="gray",
                line_height="1.6",
            ),
            rx.spacer(),
            # Metrics
            rx.hstack(
                rx.vstack(
                    rx.text("RISK LEVEL", size="1", color="gray"),
                    rx.text(
                        rx.cond(
                            framework.complexity == "beginner-friendly", "Low", "High"
                        ),
                        size="2",
                        weight="bold",
                        color=rx.cond(
                            framework.complexity == "beginner-friendly", "green", "red"
                        ),
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text("INDUSTRY", size="1", color="gray"),
                    rx.text(framework.industry, size="2", weight="bold"),
                    spacing="1",
                    align="start",
                ),
                width="100%",
            ),
            # Footer
            rx.hstack(
                rx.text(framework.author, size="1", color="gray"),
                rx.spacer(),
                rx.link(
                    rx.hstack(
                        rx.text("VIEW ASSETS", size="1", weight="medium"),
                        rx.icon("arrow-right", size=12),
                        spacing="1",
                    ),
                    color="violet",
                ),
                width="100%",
                align="center",
            ),
            spacing="3",
            width="100%",
            height="100%",
        ),
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        min_height="280px",
        cursor="pointer",
    )
