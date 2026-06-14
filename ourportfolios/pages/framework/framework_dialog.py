"""Framework detail dialog."""

from typing import cast

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.ui.primitives import (
    badge,
    body_text,
    muted_text,
    spacer,
    subheading,
)
from ourportfolios.ui.theme import BUTTON_GHOST, TEXT_PRIMARY, white


def metric_badge(metric: dict[str, object]) -> rx.Component:
    # metric is a Reflex Var inside rx.foreach — must use [] not .get()
    return badge(metric["name"], color_variant="gray")


def framework_dialog() -> rx.Component:
    content = rx.vstack(
        # Header
        rx.vstack(
            rx.heading(
                FrameworkState.selected_framework.title,
                size=rx.breakpoints(initial="5", sm="6", lg="8"),
                weight="bold",
                color=TEXT_PRIMARY,
            ),
            rx.hstack(
                muted_text("by"),
                body_text(
                    FrameworkState.selected_framework.author,
                    weight="bold",
                ),
                spacing="2",
            ),
            spacing="2",
            width="100%",
        ),
        # Badges / source link
        rx.hstack(
            badge(FrameworkState.selected_framework.scope, color_variant="gray"),
            rx.cond(
                FrameworkState.selected_framework.complexity == "complex",
                badge(FrameworkState.selected_framework.complexity, color_variant="red"),
                badge(FrameworkState.selected_framework.complexity, color_variant="green"),
            ),
            rx.cond(
                FrameworkState.selected_framework.source_name,
                rx.link(
                    rx.hstack(
                        body_text("View Source"),
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
        # Scrollable body — this is the ONLY scroll container
        rx.scroll_area(
            rx.vstack(
                subheading(
                    FrameworkState.selected_framework.description,
                    line_height="1.8",
                    color=white(0.7),
                ),
                rx.cond(
                    FrameworkState.selected_framework_has_metrics,
                    rx.vstack(
                        subheading(
                            "Framework Metrics",
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
        # Footer
        rx.hstack(
            spacer(),
            rx.button(
                rx.hstack(
                    rx.text("Select This Framework"),
                    rx.icon("arrow-right", size=18),
                    spacing="2",
                ),
                on_click=FrameworkState.select_and_navigate_framework,
                size="3",
                style=BUTTON_GHOST,
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
