import reflex as rx

# Shared base for all right-column and market overview cards
_GLASS_BG = "rgba(255, 255, 255, 0.03)"
_GLASS_BORDER = "1px solid rgba(255, 255, 255, 0.07)"
_GLASS_HOVER_BG = "rgba(255, 255, 255, 0.055)"
_GLASS_HOVER_BORDER = "rgba(255, 255, 255, 0.13)"


def glass_card(*children: rx.Component, **props: object) -> rx.Component:
    padding = props.pop("padding", "1rem")
    border_radius = props.pop("border_radius", "0.875rem")
    background = props.pop("background", _GLASS_BG)
    border = props.pop("border", _GLASS_BORDER)
    backdrop_filter = props.pop("backdrop_filter", "blur(0.75rem)")
    _hover = props.pop(
        "_hover",
        {
            "background": _GLASS_HOVER_BG,
            "border_color": _GLASS_HOVER_BORDER,
        },
    )
    # Only set default transition if caller didn't already pass one
    if "transition" not in props:
        props["transition"] = "all 0.15s ease"
    return rx.box(
        *children,
        padding=padding,
        border_radius=border_radius,
        background=background,
        backdrop_filter=backdrop_filter,
        border=border,
        _hover=_hover,
        **props,
    )


def card_wrapper(*content: rx.Component, **props: object) -> rx.Component:
    return rx.card(
        *content,
        border="none",
        background_color="transparent",
        spacing="4",
        **props,
    )
