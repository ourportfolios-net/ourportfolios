import reflex as rx

from ourportfolios.ui.tokens import SPACE_2XL


def pct_change_badge(diff: float):
    color_scheme = rx.cond(diff > 0, "green", rx.cond(diff < 0, "red", "gray"))

    return rx.badge(
        rx.flex(
            rx.cond(
                diff > 0,
                rx.icon(tag="arrow_up", size=12),
                rx.cond(
                    diff < 0,
                    rx.icon(tag="arrow_down", size=12),
                    rx.icon(tag="minus", size=12),
                ),
            ),
            rx.hstack(
                rx.text(
                    rx.cond(diff > 0, "+", ""),
                    diff,
                    "%",
                    size="1",
                    weight="medium",
                    white_space="nowrap",
                ),
                spacing="0",
                align="center",
            ),
            spacing="1",
            align="center",
            justify="center",
            width="100%",
        ),
        color_scheme=color_scheme,
        size="1",
        variant="soft",
        padding="2px 6px",  # Use fixed pixels for consistent UI
        height=SPACE_2XL,  # Use rem or em for accessibility/consistency
        min_width="fit-content",
        flex_shrink="0",
    )
