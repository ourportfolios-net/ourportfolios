"""Common dialog component with consistent styling and close button."""

import reflex as rx


def common_dialog(
    content: rx.Component,
    is_open: bool,
    on_close,
    on_open_change=None,
    width: str = "60vw",
    height: str = "58vh",
    max_width: str | None = None,
    padding: str = "2rem",
    title: str | None = None,
    title_size: str = "6",
    show_close_button: bool = True,
) -> rx.Component:
    """
    A reusable dialog component with a close button in the top-left corner.

    Args:
        content: The main content to display in the dialog
        is_open: Boolean or condition determining if dialog is open
        on_close: Function to call when closing the dialog
        on_open_change: Optional function to call when dialog open state changes
        width: Width of the dialog (default: "60vw")
        height: Height of the dialog (default: "58vh")
        max_width: Maximum width of the dialog (optional)
        padding: Padding inside the dialog (default: "2rem")
        title: Optional title text to display at the top
        title_size: Size of the title text (default: "6")
        show_close_button: Whether to show the X close button (default: True)

    Returns:
        A dialog component wrapped in rx.cond for conditional rendering
    """

    # Build the style dict
    style = {
        "width": width,
        "height": height,
        "padding": padding,
    }
    if max_width:
        style["maxWidth"] = max_width

    # Build the header with close button and optional title
    header_content = []

    if show_close_button:
        close_button = rx.dialog.close(
            rx.text(
                rx.icon("x"),
                on_click=on_close,
                style={
                    "cursor": "pointer",
                    "userSelect": "none",
                    "color": rx.color("accent", 10),
                    "_hover": {
                        "color": rx.color("accent", 7),
                    },
                },
            ),
        )
        header_content.append(close_button)

    if title:
        if show_close_button:
            header_content.append(rx.spacer())
        header_content.append(
            rx.text(
                title,
                weight="medium",
                size=title_size,
            )
        )

    # Build the dialog structure
    dialog_content = []

    # Add header if there's any header content
    if header_content:
        dialog_content.append(
            rx.hstack(
                *header_content,
                width="100%",
                padding_bottom="1rem",
                align="center",
                justify="between" if len(header_content) > 1 else "start",
            )
        )

    # Add main content
    dialog_content.append(content)

    return rx.cond(
        is_open,
        rx.dialog.root(
            rx.dialog.trigger(rx.button("hidden", style={"display": "none"})),
            rx.dialog.content(
                rx.vstack(
                    *dialog_content,
                    spacing="4",
                    align="start",
                    width="100%",
                    height="100%",
                ),
                style=style,
            ),
            open=True,
            on_open_change=on_open_change if on_open_change else on_close,
        ),
        None,
    )
