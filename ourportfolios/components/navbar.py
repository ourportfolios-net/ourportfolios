"""Navigation bar component."""

import reflex as rx
from .search_bar import search_bar


def _nav_link(label: str, href: str) -> rx.Component:
    """A simple nav link without dropdown."""
    return rx.link(
        label,
        href=href,
        font_size="14px",
        font_weight="400",
        color="rgba(255, 255, 255, 0.5)",
        text_decoration="none",
        _hover={"color": "white"},
        transition="color 0.2s",
    )


def _dropdown_item(icon: str, label: str, description: str, href: str) -> rx.Component:
    """A single item inside a hover dropdown panel."""
    return rx.link(
        rx.hstack(
            rx.icon(
                tag=icon,
                size=18,
                color=rx.color("accent", 9),
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    label,
                    font_size="14px",
                    font_weight="500",
                    color="white",
                ),
                rx.text(
                    description,
                    font_size="12px",
                    color="rgba(255, 255, 255, 0.45)",
                    line_height="1.4",
                ),
                spacing="1",
            ),
            spacing="3",
            align="start",
            padding="10px 12px",
            border_radius="8px",
            _hover={"background": "rgba(255, 255, 255, 0.06)"},
            transition="background 0.15s",
            width="100%",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def _nav_dropdown(label: str, content: rx.Component) -> rx.Component:
    """A nav link that opens a hover card dropdown panel."""
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.text(
                    label,
                    font_size="14px",
                    font_weight="400",
                ),
                rx.icon(
                    tag="chevron-down",
                    size=14,
                ),
                spacing="1",
                align="center",
                color="rgba(255, 255, 255, 0.5)",
                _hover={"color": "white"},
                transition="color 0.2s",
                cursor="pointer",
            ),
        ),
        rx.hover_card.content(
            content,
            side="bottom",
            align="start",
            side_offset=32,
            overflow="visible",
            background="rgba(17, 17, 19, 0.95)",
            backdrop_filter="blur(24px)",
            border=f"1px solid {rx.color('gray', 5)}",
            border_radius="12px",
            padding="8px",
            box_shadow="0 16px 48px rgba(0, 0, 0, 0.45)",
        ),
        open_delay=80,
        close_delay=200,
    )


def _analyze_dropdown() -> rx.Component:
    return rx.vstack(
        _dropdown_item(
            icon="line-chart",
            label="Market",
            description="Market overview and trends",
            href="/analyze",
        ),
        _dropdown_item(
            icon="factory",
            label="Industries",
            description="Explore sectors and industries",
            href="/select",
        ),
        _dropdown_item(
            icon="git-compare-arrows",
            label="Compare Tickers",
            description="Side-by-side ticker comparison",
            href="/analyze/compare",
        ),
        spacing="1",
        width="280px",
    )


def _about_dropdown() -> rx.Component:
    return rx.vstack(
        _dropdown_item(
            icon="users",
            label="ourteam",
            description="Meet the people behind ourportfolios",
            href="/about/team",
        ),
        _dropdown_item(
            icon="briefcase",
            label="ourportfolios",
            description="Learn more about the project",
            href="/about",
        ),
        spacing="1",
        width="280px",
    )


def navbar() -> rx.Component:
    """Navigation bar with logo, links, and hover dropdowns."""
    bar = rx.box(
        rx.hstack(
            rx.hstack(
                rx.text(
                    "ourportfolios",
                    font_size="1.25rem",
                    font_weight="600",
                    letter_spacing="-0.02em",
                    user_select="none",
                ),
                _nav_link("Frameworks", "/framework"),
                _nav_link("Portfolio", "/portfolio-management"),
                _nav_dropdown("Analyze", _analyze_dropdown()),
                _nav_dropdown("About", _about_dropdown()),
                spacing="6",
                align="center",
            ),
            search_bar(),
            align="center",
            justify="between",
            width="100%",
            padding_x="2rem",
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="50",
        padding_y="1rem",
        background="rgba(10, 10, 10, 0.4)",
        backdrop_filter="blur(32px)",
        border_bottom="1px solid rgba(255, 255, 255, 0.05)",
    )

    spacer = rx.box(height="4rem", width="100%")
    return rx.vstack(bar, spacer)
