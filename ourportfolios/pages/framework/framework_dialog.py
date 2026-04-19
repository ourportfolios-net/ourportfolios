"""Framework detail dialog."""

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.framework.state import FrameworkState
from ourportfolios.styles import BTN_GHOST, white


def metric_badge(metric):
    return rx.badge(
        metric["name"],
        variant="soft",
        color_scheme="gray",
        size="2",
        border_radius="0.375rem",
    )


def framework_dialog():
    content = rx.vstack(
        rx.vstack(
            rx.heading(
                FrameworkState.selected_framework.title,
                size="8",
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
                    href=rx.cond(
                        FrameworkState.selected_framework.source_url,
                        FrameworkState.selected_framework.source_url,
                        "#",
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
        rx.scroll_area(
            rx.vstack(
                rx.text(
                    FrameworkState.selected_framework.description,
                    size="3",
                    line_height="1.8",
                    color=white(0.7),
                ),
                rx.cond(
                    FrameworkState.selected_framework.metrics.length() > 0,
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
            height="100%",
            width="100%",
        ),
        rx.divider(color=white(0.07)),
        rx.hstack(
            rx.button(
                "Cancel",
                on_click=FrameworkState.close_dialog,
                size="3",
                **BTN_GHOST,
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.text("Select This Framework"),
                    rx.icon("arrow-right", size=18),
                    spacing="2",
                ),
                on_click=lambda: FrameworkState.select_and_navigate_framework(),
                size="3",
                **BTN_GHOST,
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
        height="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=FrameworkState.show_dialog,
            on_close=FrameworkState.close_dialog,
            on_open_change=FrameworkState.handle_dialog_open,
            width="65vw",
            height="70vh",
            max_width="56.25rem",
        ),
    )
