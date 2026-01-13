"""Landing page with bento grid, showcase cards, and scroll animations."""

import reflex as rx

from .components.plasma import plasma
from .components.shiny_text import shiny_text
from .components.magic_bento import magic_bento_card
from .components.scroll_reveal import scroll_reveal
from .components.card_swap import card_swap, card
from ...utils.session_manager import SessionIsolatedStateMixin
from ...components.navbar import navbar


class LandingState(SessionIsolatedStateMixin, rx.State):
    """State for landing page."""

    def on_mount(self):
        super().on_mount()

    def on_unmount(self):
        super().on_unmount()


def badge_button(text: str, **props) -> rx.Component:
    """Create a badge-style button with pulsing dot indicator."""
    padding_x = props.pop("padding_x", "1rem")
    padding_y = props.pop("padding_y", "0.375rem")

    return rx.button(
        rx.hstack(
            rx.box(
                width="0.25rem",
                height="0.25rem",
                border_radius="9999px",
                background="#7C3AED",
                animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            ),
            rx.text(
                text,
                font_size="0.625rem",
                letter_spacing="0.2em",
                text_transform="uppercase",
            ),
            spacing="2",
            align="center",
        ),
        padding_x=padding_x,
        padding_y=padding_y,
        border_radius="0.75rem",
        background="rgba(255, 255, 255, 0.03)",
        backdrop_filter="blur(24px)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        _hover={
            "background": "rgba(255, 255, 255, 0.08)",
            "border": "1px solid rgba(255, 255, 255, 0.1)",
        },
        transition="all 0.2s",
        **props,
    )


def hero_section() -> rx.Component:
    """Hero section with plasma background."""
    return rx.box(
        rx.box(
            plasma(
                color="#7C3AED",
                speed=0.8,
                direction="forward",
                scale=2,
                opacity=0.15,
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
                        speed=3,
                        color="#8a8a8a",
                        shine_color="#ffffff",
                        spread=120,
                        direction="left",
                        yoyo=False,
                        delay=2,
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
                    rx.button(
                        rx.hstack(
                            rx.text("Start for free"),
                            rx.icon("chevron-right", size=18),
                            spacing="2",
                            align="center",
                        ),
                        size="3",
                        background="white",
                        color="black",
                        border_radius="0.75rem",
                        font_weight="600",
                        padding_x="2rem",
                        padding_y="0.875rem",
                        _hover={"background": "rgba(255, 255, 255, 0.9)"},
                        transition="all 0.2s",
                    ),
                    badge_button(
                        "Contact us",
                        size="3",
                        padding_x="2rem",
                        padding_y="0.875rem",
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


def showcase_section() -> rx.Component:
    """Showcase section with CardSwap demo."""
    return scroll_reveal(
        rx.center(
            rx.box(
                rx.hstack(
                    rx.vstack(
                        shiny_text(
                            text="Card stacks have never looked so good",
                            speed=3,
                            color="#ffffff",
                            shine_color="#ffffff",
                            spread=120,
                            direction="left",
                            yoyo=False,
                            delay=0,
                            font_size=["2rem", "2.5rem", "3rem"],
                            font_weight="600",
                            line_height="1.2",
                            letter_spacing="-0.02em",
                        ),
                        rx.text(
                            "Just look at it go!",
                            font_size=["1rem", "1.125rem"],
                            color="rgba(255, 255, 255, 0.4)",
                            margin_top="2rem",
                            font_weight="300",
                            line_height="1.5",
                        ),
                        align="start",
                        spacing="0",
                        flex="1",
                        max_width="30rem",
                        min_width="22rem",
                    ),
                    rx.box(
                        rx.box(
                            card_swap(
                                card(
                                    rx.box(
                                        rx.hstack(
                                            rx.icon(
                                                "file_sliders",
                                                size=20,
                                                color="rgba(255, 255, 255, 0.5)",
                                            ),
                                            rx.heading(
                                                "Customizable",
                                                size="4",
                                                font_weight="500",
                                                letter_spacing="0.05em",
                                                text_transform="uppercase",
                                            ),
                                            spacing="3",
                                            align="center",
                                            padding="1.5rem",
                                        ),
                                        rx.box(
                                            rx.center(
                                                rx.vstack(
                                                    rx.heading(
                                                        "Fully Customizable",
                                                        size="5",
                                                        font_weight="600",
                                                        letter_spacing="-0.02em",
                                                        margin_bottom="0.75rem",
                                                    ),
                                                    rx.text(
                                                        "Tailor every aspect to match your workflow.",
                                                        font_size="0.875rem",
                                                        color="rgba(255, 255, 255, 0.6)",
                                                        line_height="1.6",
                                                        text_align="center",
                                                    ),
                                                    align="center",
                                                    spacing="0",
                                                ),
                                                width="100%",
                                                height="100%",
                                            ),
                                            padding="2rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="transparent",
                                        backdrop_filter="blur(20px)",
                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                        border_radius="1.5rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                card(
                                    rx.box(
                                        rx.hstack(
                                            rx.box(
                                                width="1.25rem",
                                                height="1.25rem",
                                                border_radius="9999px",
                                                background="rgba(255, 255, 255, 0.5)",
                                            ),
                                            rx.heading(
                                                "Smooth",
                                                size="4",
                                                font_weight="500",
                                                letter_spacing="0.05em",
                                                text_transform="uppercase",
                                            ),
                                            spacing="3",
                                            align="center",
                                            padding="1.5rem",
                                        ),
                                        rx.box(
                                            rx.hstack(
                                                rx.vstack(
                                                    rx.box(
                                                        rx.box(
                                                            rx.text(
                                                                "01",
                                                                font_size="2rem",
                                                                font_weight="900",
                                                                color="rgba(255, 255, 255, 0.1)",
                                                                margin_bottom="0.5rem",
                                                            ),
                                                            rx.text(
                                                                "Fluid Interface",
                                                                font_size="0.875rem",
                                                                font_weight="500",
                                                                letter_spacing="-0.02em",
                                                            ),
                                                        ),
                                                        height="7rem",
                                                        background="rgba(255, 255, 255, 0.02)",
                                                        border="1px solid rgba(255, 255, 255, 0.06)",
                                                        border_radius="0.875rem",
                                                        padding="1.25rem",
                                                    ),
                                                    rx.hstack(
                                                        rx.box(
                                                            rx.center(
                                                                rx.box(
                                                                    rx.box(
                                                                        width="66.67%",
                                                                        height="100%",
                                                                        background="#7C3AED",
                                                                        border_radius="9999px",
                                                                        box_shadow="0 0 6px rgba(124, 58, 237, 0.5)",
                                                                    ),
                                                                    width="2rem",
                                                                    height="0.175rem",
                                                                    background="rgba(255, 255, 255, 0.1)",
                                                                    border_radius="9999px",
                                                                    position="relative",
                                                                ),
                                                                height="100%",
                                                            ),
                                                            flex="1",
                                                            height="4rem",
                                                            background="rgba(255, 255, 255, 0.02)",
                                                            border="1px solid rgba(255, 255, 255, 0.05)",
                                                            border_radius="0.875rem",
                                                        ),
                                                        rx.box(
                                                            flex="1",
                                                            height="4rem",
                                                            background="rgba(255, 255, 255, 0.02)",
                                                            border="1px solid rgba(255, 255, 255, 0.05)",
                                                            border_radius="0.875rem",
                                                        ),
                                                        spacing="3",
                                                        width="100%",
                                                    ),
                                                    spacing="3",
                                                    flex="1",
                                                ),
                                                rx.vstack(
                                                    rx.vstack(
                                                        rx.box(
                                                            height="0.25rem",
                                                            width="50%",
                                                            background="rgba(255, 255, 255, 0.1)",
                                                            border_radius="9999px",
                                                        ),
                                                        rx.box(
                                                            height="0.25rem",
                                                            width="75%",
                                                            background="rgba(255, 255, 255, 0.05)",
                                                            border_radius="9999px",
                                                        ),
                                                        rx.box(
                                                            height="0.25rem",
                                                            width="66.67%",
                                                            background="rgba(255, 255, 255, 0.05)",
                                                            border_radius="9999px",
                                                        ),
                                                        spacing="3",
                                                    ),
                                                    rx.spacer(),
                                                    rx.center(
                                                        rx.icon(
                                                            "coins",
                                                            size=28,
                                                            color="rgba(255, 255, 255, 0.1)",
                                                        ),
                                                        width="100%",
                                                        aspect_ratio="1",
                                                        border_radius="0.625rem",
                                                        background="linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, transparent 100%)",
                                                        border="1px solid rgba(255, 255, 255, 0.05)",
                                                    ),
                                                    spacing="3",
                                                    flex="1",
                                                    background="rgba(255, 255, 255, 0.02)",
                                                    border="1px solid rgba(255, 255, 255, 0.05)",
                                                    border_radius="0.875rem",
                                                    padding="1.25rem",
                                                    max_width="10rem",
                                                ),
                                                spacing="3",
                                                align="stretch",
                                                width="100%",
                                                height="100%",
                                            ),
                                            padding="1.25rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="transparent",
                                        backdrop_filter="blur(20px)",
                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                        border_radius="1.5rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                card(
                                    rx.box(
                                        rx.hstack(
                                            rx.text(
                                                "</> ",
                                                font_size="1rem",
                                                color="rgba(255, 255, 255, 0.5)",
                                            ),
                                            rx.heading(
                                                "Reliable",
                                                size="4",
                                                font_weight="500",
                                                letter_spacing="0.05em",
                                                text_transform="uppercase",
                                            ),
                                            spacing="3",
                                            align="center",
                                            padding="1.5rem",
                                        ),
                                        rx.box(
                                            rx.center(
                                                rx.vstack(
                                                    rx.heading(
                                                        "Reliable Performance",
                                                        size="5",
                                                        font_weight="600",
                                                        letter_spacing="-0.02em",
                                                        margin_bottom="0.75rem",
                                                    ),
                                                    rx.text(
                                                        "99.9% uptime with enterprise-grade infrastructure.",
                                                        font_size="0.8rem",
                                                        color="rgba(255, 255, 255, 0.6)",
                                                        line_height="1.6",
                                                        text_align="center",
                                                        margin_bottom="1.5rem",
                                                    ),
                                                    rx.hstack(
                                                        rx.vstack(
                                                            rx.text(
                                                                "99.9%",
                                                                font_size="1.75rem",
                                                                font_weight="700",
                                                                color="#7C3AED",
                                                            ),
                                                            rx.text(
                                                                "Uptime",
                                                                font_size="0.7rem",
                                                                color="rgba(255, 255, 255, 0.4)",
                                                            ),
                                                            spacing="1",
                                                            align="center",
                                                        ),
                                                        rx.vstack(
                                                            rx.text(
                                                                "<50ms",
                                                                font_size="1.75rem",
                                                                font_weight="700",
                                                                color="#7C3AED",
                                                            ),
                                                            rx.text(
                                                                "Latency",
                                                                font_size="0.7rem",
                                                                color="rgba(255, 255, 255, 0.4)",
                                                            ),
                                                            spacing="1",
                                                            align="center",
                                                        ),
                                                        rx.vstack(
                                                            rx.text(
                                                                "24/7",
                                                                font_size="1.75rem",
                                                                font_weight="700",
                                                                color="#7C3AED",
                                                            ),
                                                            rx.text(
                                                                "Support",
                                                                font_size="0.7rem",
                                                                color="rgba(255, 255, 255, 0.4)",
                                                            ),
                                                            spacing="1",
                                                            align="center",
                                                        ),
                                                        spacing="5",
                                                    ),
                                                    align="center",
                                                    spacing="0",
                                                ),
                                                width="100%",
                                                height="100%",
                                            ),
                                            padding="1.75rem",
                                        ),
                                        width="100%",
                                        height="100%",
                                        background="transparent",
                                        backdrop_filter="blur(20px)",
                                        border="1px solid rgba(255, 255, 255, 0.08)",
                                        border_radius="1.5rem",
                                        display="flex",
                                        flex_direction="column",
                                    ),
                                ),
                                width=550,
                                height=400,
                                card_distance=40,
                                vertical_distance=45,
                                delay=4000,
                                pause_on_hover=True,
                                skew_amount=0,
                                easing="elastic",
                            ),
                            style={"transformStyle": "preserve-3d"},
                        ),
                        width=["100%", "100%", "650px"],
                        max_width="650px",
                        min_height="600px",
                        display="flex",
                        justify_content="center",
                        align_items="flex-start",
                        padding_top="2rem",
                        margin_left=["0", "0", "3rem"],
                    ),
                    spacing="0",
                    align="center",
                    width="100%",
                    max_width="1400px",
                    padding_x=["1.5rem", "2rem", "4rem"],
                    justify="center",
                    gap=["4rem", "5rem", "6rem"],
                    flex_direction=["column", "column", "row"],
                ),
                width="100%",
                display="flex",
                justify_content="center",
                overflow="hidden",
            ),
            width="100%",
            padding_y="10rem",
            margin_top="6rem",
        ),
    )


def bento_section() -> rx.Component:
    """Bento grid section with feature cards."""
    return rx.center(
        rx.vstack(
            scroll_reveal(
                rx.vstack(
                    rx.heading(
                        "The Magic Bento",
                        size="8",
                        font_weight="600",
                        letter_spacing="-0.02em",
                        margin_bottom="1.5rem",
                    ),
                    rx.text(
                        "Simple, focused tools designed for the modern investor and developer.",
                        font_size="1.125rem",
                        color="rgba(255, 255, 255, 0.4)",
                        font_weight="300",
                        line_height="1.5",
                    ),
                    align="center",
                    max_width="32rem",
                    margin_bottom="4rem",
                ),
            ),
            scroll_reveal(
                rx.box(
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "bar-chart-3",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Analytics",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Insights with pixel precision.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 3"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "layout-dashboard",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Overview",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Central data console.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "3 / 5"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "zap", size=24, color="rgba(255, 255, 255, 0.5)"
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="1.5rem",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading(
                                    "Automation",
                                    size="5",
                                    font_weight="600",
                                    margin_bottom="0.5rem",
                                ),
                                rx.text(
                                    "Streamline every workflow.",
                                    font_size="0.875rem",
                                    color="rgba(255, 255, 255, 0.3)",
                                    line_height="1.5",
                                ),
                                spacing="0",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="18.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.box(
                                rx.center(
                                    rx.icon(
                                        "users",
                                        size=24,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="3rem",
                                    height="3rem",
                                    border_radius="1rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                margin_bottom="2rem",
                            ),
                            rx.heading(
                                "Collaboration",
                                size="6",
                                font_weight="600",
                                margin_bottom="1rem",
                            ),
                            rx.text(
                                "Seamless teamwork across global borders with real-time syncing.",
                                font_size="1rem",
                                color="rgba(255, 255, 255, 0.3)",
                                max_width="17.5rem",
                                line_height="1.5",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        padding="3rem",
                        min_height="25rem",
                        grid_column=["1 / -1", "1 / -1", "1 / 5"],
                        position="relative",
                        overflow="hidden",
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.hstack(
                                rx.center(
                                    rx.icon(
                                        "shield",
                                        size=20,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.5rem",
                                    height="2.5rem",
                                    border_radius="0.75rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                rx.heading(
                                    "Security",
                                    size="4",
                                    font_weight="600",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.text(
                                "Enterprise encryption.",
                                font_size="0.75rem",
                                color="rgba(255, 255, 255, 0.3)",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="11.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    magic_bento_card(
                        rx.vstack(
                            rx.hstack(
                                rx.center(
                                    rx.icon(
                                        "plug",
                                        size=20,
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    width="2.5rem",
                                    height="2.5rem",
                                    border_radius="0.75rem",
                                    background="rgba(255, 255, 255, 0.05)",
                                ),
                                rx.heading(
                                    "Connect",
                                    size="4",
                                    font_weight="600",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.text(
                                "Universal API access.",
                                font_size="0.75rem",
                                color="rgba(255, 255, 255, 0.3)",
                            ),
                            spacing="0",
                            justify="between",
                            height="100%",
                        ),
                        padding="2.5rem",
                        min_height="11.75rem",
                        grid_column=["1 / -1", "1 / -1", "5 / 7"],
                    ),
                    display="grid",
                    grid_template_columns=["1fr", "1fr", "repeat(6, 1fr)"],
                    gap="1.5rem",
                    width="100%",
                    max_width="80rem",
                ),
                delay=0.1,
            ),
            align="center",
            width="100%",
            padding_x="1.5rem",
        ),
        width="100%",
        padding_y="10rem",
    )


def cta_section() -> rx.Component:
    """Call-to-action section."""
    return scroll_reveal(
        rx.center(
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Ready to build the future?",
                        size="8",
                        font_weight="600",
                        letter_spacing="-0.02em",
                        line_height="1.2",
                        margin_bottom="2rem",
                        text_align="center",
                    ),
                    rx.hstack(
                        rx.button(
                            "Start for free",
                            size="3",
                            background="white",
                            color="black",
                            border_radius="0.75rem",
                            font_weight="700",
                            padding_x="2.5rem",
                            padding_y="1rem",
                            _hover={"transform": "scale(1.05)"},
                            transition="all 0.2s",
                        ),
                        badge_button(
                            "Talk to Sales",
                            size="3",
                            padding_x="2.5rem",
                            padding_y="1rem",
                            font_weight="700",
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
                padding="4rem",
                background="rgba(255, 255, 255, 0.03)",
                backdrop_filter="blur(24px)",
                border="1px solid rgba(255, 255, 255, 0.05)",
                border_radius="3rem",
                position="relative",
                overflow="hidden",
                _before={
                    "content": '""',
                    "position": "absolute",
                    "inset": "0",
                    "background": "linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, transparent 100%)",
                    "opacity": "0.3",
                    "z_index": "0",
                },
            ),
            width="100%",
            padding_x="2rem",
            padding_y="8rem",
        ),
    )


def footer() -> rx.Component:
    """Footer component."""
    return scroll_reveal(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "ourportfolios",
                        font_size="1.25rem",
                        font_weight="600",
                        letter_spacing="-0.02em",
                    ),
                    rx.text(
                        "© 2024 ourportfolios. Built for precision.",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.2)",
                    ),
                    spacing="4",
                    align="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        "Privacy",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "Terms",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "Twitter",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    rx.link(
                        "GitHub",
                        href="#",
                        font_size="0.625rem",
                        letter_spacing="0.15em",
                        text_transform="uppercase",
                        color="rgba(255, 255, 255, 0.4)",
                        _hover={"color": "white"},
                        transition="color 0.2s",
                    ),
                    spacing="7",
                    wrap="wrap",
                ),
                justify="between",
                align="start",
                flex_direction=["column", "row"],
                gap="4rem",
                width="100%",
                max_width="80rem",
                margin="0 auto",
                padding_x="2.5rem",
            ),
            border_top="1px solid rgba(255, 255, 255, 0.05)",
            padding_y="5rem",
            padding_x="2.5rem",
        ),
    )


@rx.page(route="/", on_load=LandingState.on_mount)
def index() -> rx.Component:
    """Main landing page."""
    return rx.box(
        navbar(),
        hero_section(),
        rx.box(id="showcase"),
        showcase_section(),
        rx.box(id="features"),
        bento_section(),
        rx.box(id="pricing"),
        cta_section(),
        footer(),
        on_unmount=LandingState.on_unmount,
        background="#050505",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
