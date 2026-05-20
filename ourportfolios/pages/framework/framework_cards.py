"""Framework cards and sidebar components."""

import reflex as rx

from ourportfolios.pages.framework.state import (
    CategoryModel,
    FrameworkModel,
    FrameworkState,
)
from ourportfolios.ui.primitives import (
    hstack,
    pill_toggle,
    skeleton_box,
    spacer,
    vstack,
)
from ourportfolios.ui.theme import (
    CARD_STYLE,
    accent_button,
    white,
)
from ourportfolios.ui.theme.surfaces import RADIUS_PILL

_DESCRIPTION_CLAMP = {
    "-webkit-line-clamp": "3",
    "-webkit-box-orient": "vertical",
}


def _skel(w: str, h: str) -> rx.Component:
    return skeleton_box(width=w, height=h)


def skeleton_card() -> rx.Component:
    return rx.box(
        vstack(
            rx.box(
                spacer(),
                _skel("4.375rem", "1.125rem"),
                width="100%",
                display="flex",
                justify_content="flex-end",
            ),
            vstack(
                _skel("60%", "1.25rem"),
                _skel("100%", "0.875rem"),
                _skel("80%", "0.875rem"),
                spacing="2",
                width="100%",
                align="start",
            ),
            spacer(),
            hstack(
                vstack(
                    _skel("2.8125rem", "0.625rem"),
                    _skel("5rem", "0.875rem"),
                    spacing="1",
                    align="start",
                ),
                spacer(),
                _skel("5.625rem", "0.875rem"),
                width="100%",
                align="center",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        style=CARD_STYLE,
    )


def category_filter_button(category: CategoryModel) -> rx.Component:
    is_active = FrameworkState.active_category == category.value

    return pill_toggle(
        category.label,
        active=is_active,
        on_click=lambda: FrameworkState.set_active_category(category.value),
    )


def framework_card(framework: FrameworkModel) -> rx.Component:
    return rx.box(
        vstack(
            rx.box(
                rx.badge(
                    framework.scope,
                    variant="soft",
                    color_scheme="gray",
                    size="1",
                    border_radius=RADIUS_PILL,
                    font_size="0.625rem",
                    letter_spacing="0.03em",
                ),
                width="100%",
                display="flex",
                justify_content="flex-end",
            ),
            vstack(
                rx.text(
                    framework.title,
                    size="4",
                    weight="bold",
                    color="white",
                    line_height="1.35",
                ),
                rx.text(
                    framework.description,
                    size="2",
                    color=white(0.38),
                    line_height="1.65",
                    display="-webkit-box",
                    overflow="hidden",
                    style=_DESCRIPTION_CLAMP,
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            spacer(),
            hstack(
                vstack(
                    rx.text(
                        "AUTHOR",
                        size="1",
                        color=white(0.2),
                        weight="bold",
                        letter_spacing="0.08em",
                    ),
                    rx.text(
                        framework.author,
                        size="2",
                        color=white(0.6),
                        weight="medium",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacer(),
                accent_button("View Framework"),
                width="100%",
                align="center",
            ),
            spacing="4",
            width="100%",
            height="100%",
        ),
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        style=CARD_STYLE,
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={
            "background": white(0.045),
            "border_color": white(0.13),
            "transform": "translateY(-1px)",
        },
    )
