import reflex as rx

# Shared base for all right-column and market overview cards
_GLASS_BG = "rgba(255, 255, 255, 0.03)"
_GLASS_BORDER = "1px solid rgba(255, 255, 255, 0.07)"
_GLASS_HOVER_BG = "rgba(255, 255, 255, 0.055)"
_GLASS_HOVER_BORDER = "rgba(255, 255, 255, 0.13)"


def glass_card(
    *children: rx.Component,
    padding: rx.Var[str] | str | dict[str, str] = "1rem",
    width: rx.Var[str] | str | dict[str, str] | None = None,
    _hover: dict[str, rx.Var[str] | str] | None = None,
    on_mount: list[rx.EventHandler] | rx.EventHandler | None = None,
) -> rx.Component:
    hover_style = (
        {
            "background": _GLASS_HOVER_BG,
            "border_color": _GLASS_HOVER_BORDER,
        }
        if _hover is None
        else _hover
    )
    return rx.box(
        *children,
        padding=padding,
        border_radius="0.875rem",
        background=_GLASS_BG,
        backdrop_filter="blur(0.75rem)",
        border=_GLASS_BORDER,
        width=width,
        _hover=hover_style,
        on_mount=on_mount,
    )


def card_wrapper(*content: rx.Component) -> rx.Component:
    return rx.card(
        *content,
        border="none",
        background_color="transparent",
        spacing="4",
    )
