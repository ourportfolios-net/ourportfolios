"""Common dialog component with consistent styling and close button."""

from dataclasses import dataclass
from typing import Any, Literal

import reflex as rx

from ourportfolios.ui.primitives import modal_panel
from ourportfolios.ui.theme.colors import TEXT_TERTIARY, white
from ourportfolios.ui.tokens import SPACE_2XL, SPACE_LG, TRANS_COLOR


@dataclass(slots=True)
class CommonDialogConfig:
    is_open: bool
    on_close: Any
    on_open_change: Any | None = None
    width: str = "60vw"
    height: str = "58vh"
    max_width: str | None = None
    padding: str = SPACE_2XL
    title: str | None = None
    title_size: Literal["1", "2", "3", "4", "5", "6", "7", "8", "9"] = "6"
    show_close_button: bool = True


def common_dialog(content: rx.Component, config: CommonDialogConfig) -> rx.Component:
    """Return reusable dialog component with a close button in the top-left corner.

    Args:
        content: The main content to display in the dialog
        config: Dialog configuration and callbacks.

    Returns:
        A dialog component wrapped in rx.cond for conditional rendering

    """
    # Build optional keyword args for max_width
    extra_props: dict[str, Any] = {}
    if config.max_width:
        extra_props["max_width"] = config.max_width

    # Build the header with close button and optional title
    header_content = []

    if config.show_close_button:
        close_button = rx.dialog.close(
            rx.text(
                rx.icon("x", size=18),
                on_click=config.on_close,
                cursor="pointer",
                user_select="none",
                color=white(0.45),
                _hover={"color": "white"},
                transition=TRANS_COLOR,
            ),
        )
        header_content.append(close_button)

    if config.title:
        if config.show_close_button:
            header_content.append(rx.spacer())
        header_content.append(
            rx.text(
                config.title,
                weight="medium",
                size=config.title_size,
                color=TEXT_TERTIARY,
            ),
        )

    # Build the dialog structure
    dialog_content = []

    # Add header if there's any header content
    if header_content:
        dialog_content.append(
            rx.hstack(
                *header_content,
                width="100%",
                padding_bottom=SPACE_LG,
                align="center",
                justify="between" if len(header_content) > 1 else "start",
            ),
        )

    # Add main content
    dialog_content.append(content)

    # Build props for dialog.content to override Radix defaults
    dialog_props: dict[str, object] = {
        "width": config.width,
        "height": config.height,
        "max_height": config.height,
        "padding": "0",
        "overflow": "hidden",
    }
    if config.max_width:
        dialog_props["max_width"] = config.max_width

    return rx.cond(
        config.is_open,
        rx.dialog.root(
            rx.dialog.content(
                modal_panel(
                    rx.vstack(
                        *dialog_content,
                        spacing="4",
                        align="start",
                        width="100%",
                        height="100%",
                    ),
                    width="100%",
                    height="100%",
                    padding=config.padding,
                    max_width=None,
                ),
                **dialog_props,
            ),
            open=True,
            on_open_change=config.on_open_change or config.on_close,
        ),
        None,
    )
