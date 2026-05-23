"""Hero section component."""

import reflex as rx

from ourportfolios.pages.landing.components import badge_button, plasma, shiny_text
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.tokens import (
    RADIUS_SM,
    SPACE_LG,
    SPACE_XL,
    TRANS_DEFAULT,
    WEIGHT_SEMIBOLD,
)

_CTA_BUTTON_STYLE = {
    "background": white(0.7),
    "color": "rgba(0, 0, 0, 0.85)",
    "border_radius": RADIUS_SM,
    "font_weight": WEIGHT_SEMIBOLD,
    "padding_x": SPACE_XL,
    "padding_y": SPACE_LG,
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.95)},
}


def hero_section() -> rx.Component:
    """Hero section with plasma background."""
    return rx.box(
        rx.box(
            plasma(
                color="#7C3AED",
                speed=0.8,
                direction="forward",
                scale=2,
                opacity=0.18,
                mouse_interactive=False,
            ),
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="0",
            style={
                "maskImage": "radial-gradient(ellipse 80% 70% at 50% 40%, black 30%, transparent 100%)",
                "WebkitMaskImage": "radial-gradient(ellipse 80% 70% at 50% 40%, black 30%, transparent 100%)",
            },
        ),
        rx.box(
            position="absolute",
            width="62.5rem",
            height="62.5rem",
            background="radial-gradient(circle, rgba(124, 58, 237, 0.04) 0%, rgba(124, 58, 237, 0) 70%)",
            pointer_events="none",
            z_index="0",
            top="-16rem",
            left="-16rem",
        ),
        rx.center(
            rx.vstack(
                rx.box(
                    shiny_text(
                        text="yourportfolio starts here!",
                        speed=1.5,
                        color=white(0.7),
                        shine_color=white(1),
                        spread=120,
                        direction="left",
                        yoyo=False,
                        delay=3,
                        font_size=["2.5rem", "3rem", "3.5rem", "4rem"],
                        font_weight="750",
                        line_height="1.1",
                        letter_spacing="-0.02em",
                    ),
                    margin_bottom="2rem",
                    max_width="56rem",
                    text_align="center",
                ),
                rx.text(
                    "Build your portfolios. We'll build ours.",
                    font_size=["1rem", "1.125rem", "1.25rem"],
                    color=white(0.4),
                    margin_bottom="3rem",
                    max_width="36rem",
                    text_align="center",
                    font_weight="300",
                    line_height="1.5",
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
                            padding_x="2rem",
                            padding_y="0.875rem",
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
            min_height="90vh",
            padding_top="8rem",
            padding_bottom="5rem",
            padding_x="1.5rem",
        ),
        position="relative",
        overflow="hidden",
        width="100%",
    )
