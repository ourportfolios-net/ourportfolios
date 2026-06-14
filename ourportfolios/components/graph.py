import reflex as rx

from ourportfolios.ui.primitives.badge import badge


def _badge_content(diff: float) -> rx.Component:
    return rx.flex(
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
    )


def pct_change_badge(diff: float):
    return rx.cond(
        diff > 0,
        badge(
            _badge_content(diff),
            color_variant="green",
            min_width="fit-content",
            flex_shrink="false",
        ),
        rx.cond(
            diff < 0,
            badge(
                _badge_content(diff),
                color_variant="red",
                min_width="fit-content",
                flex_shrink="false",
            ),
            badge(
                _badge_content(diff),
                color_variant="gray",
                min_width="fit-content",
                flex_shrink="false",
            ),
        ),
    )
