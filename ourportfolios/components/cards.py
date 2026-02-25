import reflex as rx

cards = [
    {"title": "Recommend", "details": "Card 1 details", "link": "/framework"},
    {"title": "Select", "details": "Card 2 details", "link": "/select"},
    {"title": "Analyze", "details": "Card 3 details", "link": "/analyze"},
    {"title": "Simulate", "details": "Card 4 details", "link": "/simulate"},
]

# Shared base for all right-column and market overview cards
_GLASS_BG = "rgba(255, 255, 255, 0.03)"
_GLASS_BORDER = "1px solid rgba(255, 255, 255, 0.07)"
_GLASS_HOVER_BG = "rgba(255, 255, 255, 0.055)"
_GLASS_HOVER_BORDER = "rgba(255, 255, 255, 0.13)"


def glass_card(*children, **props) -> rx.Component:
    padding = props.pop("padding", "1rem")
    border_radius = props.pop("border_radius", "14px")
    background = props.pop("background", _GLASS_BG)
    border = props.pop("border", _GLASS_BORDER)
    backdrop_filter = props.pop("backdrop_filter", "blur(12px)")
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


def portfolio_card(card, idx, total):
    def get_card_position_size(idx, total):
        spread_x = 65
        spread_y = 15
        width = 23
        height = 48

        if total > 1:
            center = (idx / (total - 1)) * spread_x + (50 - spread_x / 2)
            left = center - width / 2
            left = max(0, min(left, 100 - width))
            top = (idx / (total - 1)) * spread_y
        else:
            left = 50 - width / 2
            top = 20

        return f"{top}%", f"{left}%", f"{width}%", f"{height}%"

    top, left, width, height = get_card_position_size(idx, total)
    return rx.link(
        rx.card(
            rx.text(card["title"], size="3", weight="medium"),
            rx.text(card["details"], size="2"),
            height=height,
            width=width,
            position="absolute",
            top=top,
            left=left,
            transition="transform 0.2s, box-shadow 0.2s, z-index 0.2s",
            _hover={
                "transform": "scale(1.05)",
                "z_index": "10",
                "box_shadow": "0 8px 32px rgba(0,0,0,0.25)",
            },
            padding="1.2rem",
        ),
        href=card["link"],
        style={"textDecoration": "none"},
    )


def card_wrapper(*content, style=None):
    style = style or {}
    return rx.card(
        *content,
        border="none",
        background_color="transparent",
        style=style,
        spacing="4",
    )
