"""Framework detail dialog."""

from typing import cast

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.styles import BTN_GHOST, white


def metric_badge(metric: dict[str, object]) -> rx.Component:
    # metric is a Reflex Var inside rx.foreach — must use [] not .get()
    return rx.badge(
        metric["name"],
        variant="soft",
        color_scheme="gray",
        size="2",
        border_radius="0.375rem",
    )


def framework_dialog() -> rx.Component:
    content = rx.vstack(
        # Header
        rx.vstack(
            rx.heading(
                FrameworkState.selected_framework.title,
                size=rx.breakpoints(initial="5", sm="6", lg="8"),
                weight="bold",
            ),
            rx.hstack(
                rx.text("by", size="2", color=white(0.4)),
                rx.text(
                    FrameworkState.selected_framework.author,
                    size="2",
                    weight="bold",
                ),
                spacing="2",
            ),
            spacing="2",
            width="100%",
        ),
        # Badges / source link
        rx.hstack(
            rx.badge(FrameworkState.selected_framework.scope, variant="soft", size="2"),
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
            rx.cond(
                FrameworkState.selected_framework.source_name,
                rx.link(
                    rx.hstack(
                        rx.text("View Source", size="2"),
                        rx.icon("external-link", size=13),
                        spacing="1",
                        align="center",
                    ),
                    href=cast(
                        "str",
                        rx.cond(
                            FrameworkState.selected_framework.source_url,
                            FrameworkState.selected_framework.source_url,
                            "#",
                        ),
                    ),
                    is_external=True,
                    text_decoration="none",
                    _hover={"opacity": "0.8"},
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="center",
            width="100%",
            wrap="wrap",
        ),
        rx.divider(color=white(0.07)),
        # Scrollable body — this is the ONLY scroll container
        rx.scroll_area(
            rx.vstack(
                rx.text(
                    FrameworkState.selected_framework.description,
                    size="3",
                    line_height="1.8",
                    color=white(0.7),
                ),
                rx.cond(
                    FrameworkState.selected_framework_has_metrics,
                    rx.vstack(
                        rx.text(
                            "Framework Metrics",
                            size="3",
                            weight="bold",
                            color="white",
                        ),
                        rx.box(
                            rx.foreach(
                                FrameworkState.selected_framework.metrics,
                                metric_badge,
                            ),
                            display="flex",
                            flex_wrap="wrap",
                            gap="0.5rem",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                spacing="4",
                width="100%",
            ),
            # flex="1" lets this grow to fill available height between
            # header and footer, preventing the outer dialog from scrolling.
            flex="1",
            width="100%",
            overflow_y="auto",
        ),
        rx.divider(color=white(0.07)),
        # Footer
        rx.hstack(
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.text("Select This Framework"),
                    rx.icon("arrow-right", size=18),
                    spacing="2",
                ),
                on_click=FrameworkState.select_and_navigate_framework,
                size="3",
                style=BTN_GHOST,
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
        height="100%",
        # Prevent the outer dialog container from growing its own scrollbar.
        overflow="hidden",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=cast("bool", FrameworkState.show_dialog),
            on_close=FrameworkState.close_dialog,
            on_open_change=FrameworkState.handle_dialog_open,
            width="75vw",
            height="80vh",
            max_width="68.75rem",
        ),
    )
