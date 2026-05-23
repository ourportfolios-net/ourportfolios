"""Call-to-action section."""

import reflex as rx

from ourportfolios.pages.landing.components import badge_button, scroll_reveal
from ourportfolios.ui.theme.colors import GLOW_PURPLE, TEXT_PRIMARY, white
from ourportfolios.ui.tokens import (
    BLUR_DEFAULT,
    RADIUS_MD,
    RADIUS_SM,
    SPACE_LG,
    SPACE_XL,
    TRANS_DEFAULT,
    WEIGHT_SEMIBOLD,
)

_CTA_BUTTON_STYLE = {
    "background": white(0.7),
    "color": "rgba(0, 0, 0, 0.85)",
    "border_radius": RADIUS_MD,
    "font_weight": WEIGHT_SEMIBOLD,
    "padding_x": SPACE_XL,
    "padding_y": SPACE_LG,
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.95)},
}


def cta_section() -> rx.Component:
    """Call-to-action section."""
    return scroll_reveal(
        rx.center(
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Ready to build ourportfolios?",
                        size="8",
                        font_weight="700",
                        letter_spacing="-0.02em",
                        line_height="1.2",
                        margin_bottom=SPACE_XL,
                        text_align="center",
                        color=TEXT_PRIMARY,
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                rx.hstack(
                                    rx.text("Start for free"),
                                    rx.icon("chevron-right", size=18),
                                    spacing="2",
                                    align="center",
                                ),
                                size="3",
                                style=_CTA_BUTTON_STYLE,
                            ),
                            href="/auth",
                        ),
                        rx.link(
                            badge_button(
                                "Contact us",
                                size="3",
                                padding_x=SPACE_XL,
                                padding_y=SPACE_LG,
                            ),
                            href="/contacts",
                        ),
                        spacing="4",
                        flex_direction=["column", "row"],
                    ),
                    align="center",
                    spacing="0",
                    z_index="10",
                    position="relative",
                ),
                max_width="80rem",
                width="100%",
                padding="3rem",
                background=white(0.03),
                backdrop_filter=f"blur({BLUR_DEFAULT})",
                border=f"1px solid {white(0.05)}",
                border_radius=RADIUS_SM,
                position="relative",
                overflow="hidden",
                _before={
                    "content": '""',
                    "position": "absolute",
                    "inset": "0",
                    "background": f"linear-gradient(135deg, {GLOW_PURPLE} 100%, transparent 100%)",
                    "opacity": "0.3",
                    "z_index": "0",
                },
            ),
            width="100%",
            padding_x="2rem",
            padding_y="8rem",
        ),
    )
