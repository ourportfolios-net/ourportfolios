"""Framework detail dialog."""

import reflex as rx

from .state import FrameworkState
from ...components.common_dialog import common_dialog


def metric_badge(metric):
    """Display a metric as a badge"""
    return rx.badge(
        metric["name"],
        color_scheme="violet",
        variant="soft",
        size="2",
    )


def framework_dialog():
    content = rx.vstack(
        # Header with gradient title
        rx.vstack(
            rx.heading(
                FrameworkState.selected_framework.title,
                size="8",
                weight="bold",
                style={
                    "background": "linear-gradient(135deg, #FFFFFF 0%, #A78BFA 100%)",
                    "background_clip": "text",
                    "color": "transparent",
                },
            ),
            rx.hstack(
                rx.text(
                    "by",
                    size="2",
                    color="gray",
                ),
                rx.text(
                    FrameworkState.selected_framework.author,
                    size="2",
                    weight="bold",
                    color="#8B5CF6",
                ),
                spacing="2",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        # Badges row
        rx.hstack(
            rx.hstack(
                rx.icon("info", size=14, color="gray"),
                rx.badge(
                    FrameworkState.selected_framework.scope,
                    color_scheme="plum",
                    variant="soft",
                    size="2",
                ),
                rx.badge(
                    FrameworkState.selected_framework.complexity,
                    color_scheme=rx.cond(
                        FrameworkState.selected_framework.complexity == "complex",
                        "red",
                        "green",
                    ),
                    variant="soft",
                    size="2",
                ),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.cond(
                FrameworkState.selected_framework.source_name,
                rx.link(
                    rx.hstack(
                        rx.icon("external-link", size=14),
                        rx.text("View Source", size="2", weight="medium"),
                        spacing="1",
                        align="center",
                    ),
                    href=rx.cond(
                        FrameworkState.selected_framework.source_url,
                        FrameworkState.selected_framework.source_url,
                        "#",
                    ),
                    is_external=True,
                    color="#8B5CF6",
                ),
                rx.fragment(),
            ),
            width="100%",
            align="center",
            padding_y="1em",
            style={
                "border_bottom": "1px solid rgba(139, 92, 246, 0.2)",
            },
        ),
        # Description in scroll area
        rx.scroll_area(
            rx.vstack(
                rx.text(
                    "Description",
                    size="3",
                    weight="bold",
                    color="#8B5CF6",
                ),
                rx.text(
                    FrameworkState.selected_framework.description,
                    size="3",
                    style={
                        "line_height": "1.8",
                        "color": "rgba(255, 255, 255, 0.85)",
                    },
                ),
                # Metrics section
                rx.cond(
                    FrameworkState.selected_framework.metrics.length() > 0,
                    rx.vstack(
                        rx.text(
                            "Framework Metrics",
                            size="3",
                            weight="bold",
                            color="#8B5CF6",
                            padding_top="1em",
                        ),
                        rx.box(
                            rx.foreach(
                                FrameworkState.selected_framework.metrics, metric_badge
                            ),
                            display="flex",
                            flex_wrap="wrap",
                            gap="0.5em",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={
                "width": "100%",
                "height": "100%",
                "padding_right": "1em",
            },
            scrollbars="vertical",
        ),
        # Action buttons
        rx.hstack(
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_dialog,
                variant="soft",
                color_scheme="gray",
                size="3",
                style={
                    "border_radius": "0.75em",
                },
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.text("Select This Framework", weight="bold"),
                    rx.icon("arrow-right", size=18),
                    spacing="2",
                    align="center",
                ),
                on_click=lambda: FrameworkState.select_and_navigate_framework(),
                size="3",
                color_scheme="violet",
                style={
                    "border_radius": "0.75em",
                    "background": "linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)",
                },
            ),
            spacing="3",
            width="100%",
            justify="between",
            padding_top="1em",
            style={
                "border_top": "1px solid rgba(139, 92, 246, 0.2)",
            },
        ),
        spacing="0",
        align="start",
        width="100%",
        height="100%",
    )

    return common_dialog(
        content=content,
        is_open=FrameworkState.show_dialog,
        on_close=FrameworkState.close_dialog,
        on_open_change=FrameworkState.handle_dialog_open,
        width="65vw",
        height="70vh",
        max_width="900px",
    )
