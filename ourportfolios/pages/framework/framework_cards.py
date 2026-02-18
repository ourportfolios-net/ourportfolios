"""Framework cards and sidebar components."""

import reflex as rx

from .state import FrameworkState


def skeleton_card() -> rx.Component:
    """Skeleton placeholder for a framework card while loading."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.skeleton(
                    rx.box(width="31px", height="31px"),
                    loading=True,
                    style={"border_radius": "8px"},
                ),
                rx.spacer(),
                rx.skeleton(
                    rx.box(width="70px", height="18px"),
                    loading=True,
                    style={"border_radius": "6px"},
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.skeleton(
                    rx.box(width="60%", height="20px"),
                    loading=True,
                    style={"border_radius": "6px"},
                ),
                rx.skeleton(
                    rx.box(width="100%", height="14px"),
                    loading=True,
                    style={"border_radius": "6px"},
                ),
                rx.skeleton(
                    rx.box(width="80%", height="14px"),
                    loading=True,
                    style={"border_radius": "6px"},
                ),
                rx.skeleton(
                    rx.box(width="90%", height="14px"),
                    loading=True,
                    style={"border_radius": "6px"},
                ),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            rx.vstack(
                rx.box(height="1px", width="100%", background="rgba(255,255,255,0.05)"),
                rx.hstack(
                    rx.vstack(
                        rx.skeleton(
                            rx.box(width="45px", height="10px"),
                            loading=True,
                            style={"border_radius": "4px"},
                        ),
                        rx.skeleton(
                            rx.box(width="80px", height="14px"),
                            loading=True,
                            style={"border_radius": "4px"},
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.skeleton(
                        rx.box(width="90px", height="14px"),
                        loading=True,
                        style={"border_radius": "4px"},
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        background="rgba(255,255,255,0.025)",
        border="1px solid rgba(255,255,255,0.07)",
        border_radius="14px",
        padding="1.5rem",
        min_height="240px",
    )


def category_filter_button(category):
    """Category filter button — pill shaped, clearly interactive"""
    is_active = FrameworkState.active_category == category.value

    return rx.button(
        category.label,
        on_click=lambda: FrameworkState.set_active_category(category.value),
        size="2",
        style=rx.cond(
            is_active,
            {
                "background": "rgba(139,92,246,0.18)",
                "border": "1px solid rgba(139,92,246,0.5)",
                "border_radius": "999px",
                "color": "#c4b5fd",
                "font_weight": "600",
                "font_size": "13px",
                "cursor": "pointer",
                "transition": "all 0.15s ease",
                "padding": "0 16px",
            },
            {
                "background": "transparent",
                "border": "1px solid rgba(255,255,255,0.1)",
                "border_radius": "999px",
                "color": "rgba(255,255,255,0.5)",
                "font_weight": "500",
                "font_size": "13px",
                "cursor": "pointer",
                "transition": "all 0.15s ease",
                "padding": "0 16px",
                "_hover": {
                    "background": "rgba(255,255,255,0.06)",
                    "color": "rgba(255,255,255,0.85)",
                    "border_color": "rgba(255,255,255,0.2)",
                },
            },
        ),
    )


def framework_card(framework):
    """Framework card — clean hierarchy, minimal purple, more breathing room"""

    return rx.box(
        rx.vstack(
            # Top: icon + scope badge
            rx.hstack(
                rx.box(
                    rx.icon("trending-up", size=15, color="rgba(255,255,255,0.5)"),
                    background="rgba(255,255,255,0.06)",
                    border_radius="8px",
                    padding="8px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.spacer(),
                rx.badge(
                    framework.scope,
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                    style={
                        "border_radius": "6px",
                        "font_size": "10px",
                        "letter_spacing": "0.03em",
                    },
                ),
                width="100%",
                align="center",
            ),
            # Title + description block
            rx.vstack(
                rx.text(
                    framework.title,
                    size="4",
                    weight="bold",
                    color="white",
                    line_height="1.35",
                ),
                rx.text(
                    framework.description,
                    size="2",
                    color="rgba(255,255,255,0.38)",
                    line_height="1.65",
                    style={
                        "display": "-webkit-box",
                        "-webkit-line-clamp": "3",
                        "-webkit-box-orient": "vertical",
                        "overflow": "hidden",
                    },
                ),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            # Footer divider + author + CTA
            rx.vstack(
                rx.box(height="1px", width="100%", background="rgba(255,255,255,0.05)"),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            size="1",
                            color="rgba(255,255,255,0.2)",
                            weight="bold",
                            letter_spacing="0.08em",
                        ),
                        rx.text(
                            framework.author,
                            size="2",
                            color="rgba(255,255,255,0.6)",
                            weight="medium",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.text(
                            "VIEW ASSETS", size="1", weight="bold", color="#a78bfa"
                        ),
                        rx.icon("arrow-right", size=12, color="#a78bfa"),
                        spacing="1",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        background="rgba(255,255,255,0.025)",
        border="1px solid rgba(255,255,255,0.07)",
        border_radius="14px",
        padding="1.5rem",
        cursor="pointer",
        min_height="240px",
        style={
            "transition": "all 0.15s ease",
            "_hover": {
                "background": "rgba(255,255,255,0.045)",
                "border_color": "rgba(255,255,255,0.13)",
                "transform": "translateY(-1px)",
            },
        },
    )
