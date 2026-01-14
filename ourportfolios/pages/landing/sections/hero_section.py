"""Hero section component."""

import reflex as rx

from ..components import plasma, shiny_text, badge_button


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
                mouse_interactive=True,
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
            width="1000px",
            height="1000px",
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
                        color="rgba(255, 255, 255, 0.7)",
                        shine_color="rgba(255, 255, 255, 1)",
                        spread=120,
                        direction="left",
                        yoyo=False,
                        delay=3,
                        font_size=["2.5rem", "3rem", "3.5rem", "4rem"],
                        font_weight="450",
                        line_height="1.1",
                        letter_spacing="-0.02em",
                    ),
                    margin_bottom="2rem",
                    max_width="56rem",
                    text_align="center",
                ),
                rx.text(
                    "Build wealth with precision while we build the future of investment tech.",
                    font_size=["1rem", "1.125rem", "1.25rem"],
                    color="rgba(255, 255, 255, 0.4)",
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
                            background="rgba(255, 255, 255, 0.85)",
                            color="rgba(0, 0, 0, 0.85)",
                            border_radius="0.75rem",
                            font_weight="600",
                            padding_x="2rem",
                            padding_y="0.875rem",
                            _hover={"background": "rgba(255, 255, 255, 0.9)"},
                            transition="all 0.2s",
                        ),
                        href="/home",
                    ),
                    rx.link(
                        badge_button(
                            "Contact us",
                            size="3",
                            padding_x="2rem",
                            padding_y="0.875rem",
                        ),
                        href="/contact",
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
