"""Framework detail dialog."""

import reflex as rx

from .state import FrameworkState
from ...components.dialog import common_dialog


def framework_dialog():
    content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading(
                    FrameworkState.selected_framework["title"],
                    size="7",
                    weight="bold",
                    text_align="right",
                ),
                rx.text(
                    FrameworkState.selected_framework["author"],
                    size="2",
                    color="gray",
                    text_align="right",
                ),
                align="end",
                spacing="1",
            ),
            width="100%",
            align="start",
            justify="end",
        ),
        rx.hstack(
                        rx.cond(
                            FrameworkState.selected_framework.get("source_name"),
                            rx.hstack(
                                rx.icon("book-open", size=16),
                                rx.text("Source:", weight="bold", size="2"),
                                rx.cond(
                                    FrameworkState.selected_framework.get("source_url"),
                                    rx.link(
                                        FrameworkState.selected_framework[
                                            "source_name"
                                        ],
                                        href=FrameworkState.selected_framework[
                                            "source_url"
                                        ],
                                        is_external=True,
                                        size="2",
                                    ),
                                    rx.text(
                                        FrameworkState.selected_framework[
                                            "source_name"
                                        ],
                                        size="2",
                                    ),
                                ),
                                spacing="2",
                                align="center",
                            ),
                            None,
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.badge(
                                FrameworkState.selected_framework["scope"],
                                color_scheme="plum",
                                variant="soft",
                                size="2",
                            ),
                            rx.badge(
                                FrameworkState.selected_framework["complexity"],
                                color_scheme=rx.cond(
                                    FrameworkState.selected_framework["complexity"]
                                    == "complex",
                                    "accent",
                                    "jade",
                                ),
                                variant="soft",
                                size="2",
                            ),
                            spacing="2",
                        ),
                        width="100%",
                        align="center",
                        padding_bottom="1rem",
                    ),
                    rx.scroll_area(
                        rx.blockquote(
                            FrameworkState.selected_framework["description"],
                            size="3",
                        ),
                        style={
                            "width": "100%",
                            "height": "100%",
                        },
                        scrollbars="vertical",
                    ),
                    rx.hstack(
                        rx.spacer(),
                        rx.button(
                            "Cancel",
                            on_click=FrameworkState.close_dialog,
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                        ),
                        rx.button(
                            "Select This Framework",
                            on_click=lambda: FrameworkState.select_and_navigate_framework(),
                            size="3",
                            color_scheme="violet",
                        ),
                        spacing="2",
                        width="100%",
                        justify="end",
                        padding_top="1rem",
                    ),
        spacing="4",
        align="start",
        width="100%",
        height="100%",
    )
    
    return common_dialog(
        content=content,
        is_open=FrameworkState.show_dialog,
        on_close=FrameworkState.close_dialog,
        on_open_change=FrameworkState.handle_dialog_open,
        width="60vw",
        height="58vh",
        max_width="60vw",
    )
