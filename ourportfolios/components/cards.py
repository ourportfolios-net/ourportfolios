import reflex as rx

cards = [
    {"title": "Recommend", "details": "Card 1 details", "link": "/recommend"},
    {"title": "Select", "details": "Card 2 details", "link": "/select"},
    {"title": "Analyze", "details": "Card 3 details", "link": "/analyze"},
    {"title": "Simulate", "details": "Card 4 details", "link": "/simulate"},
]


def glass_card(*children, **props) -> rx.Component:
    """Create a glassmorphism card with rounded corners.

    A reusable card component with:
    - Glass morphism effect (blur + transparency)
    - Rounded corners
    - Subtle border
    - Dark background with blur

    Args:
        *children: Child components to render inside the card
        **props: Additional props to pass to the box component

    Returns:
        rx.Component: A glassmorphism card
    """
    # Extract custom props or set defaults
    padding = props.pop("padding", "1.5rem")
    border_radius = props.pop("border_radius", "24px")
    background = props.pop("background", "rgba(20, 20, 20, 0.4)")
    border = props.pop("border", "1px solid rgba(255, 255, 255, 0.08)")
    backdrop_filter = props.pop("backdrop_filter", "blur(12px)")

    return rx.box(
        *children,
        padding=padding,
        border_radius=border_radius,
        background=background,
        backdrop_filter=backdrop_filter,
        border=border,
        **props,
    )


def portfolio_card(card, idx, total):
    def get_card_position_size(idx, total):
        spread_x = 65  # percent of parent width; lower for more overlap
        spread_y = 15  # vertical spread
        width = 23  # percent of parent width; adjust for desired overlap
        height = 48  # percent of parent height

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
            transition="transform 0.15s, box-shadow 0.2s, z-index 0.2s",
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
