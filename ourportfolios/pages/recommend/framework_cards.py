"""Framework cards and sidebar components."""

import reflex as rx

from .state import FrameworkState


def scope_button(scope: dict):
    return rx.button(
        rx.hstack(
            rx.text(scope["title"], size="3", weight="medium"),
            spacing="2",
            align="center",
            width="100%",
            justify="start",
        ),
        on_click=FrameworkState.change_scope(scope["value"]),
        variant="soft",
        color_scheme=rx.cond(
            FrameworkState.active_scope == scope["value"], "white", "gray"
        ),
        size="3",
        width="100%",
        height="3em",
        justify="start",
        padding="0.75em",
    )


def framework_card(framework: dict):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(framework["title"], size="6", weight="bold"),
                rx.spacer(),
                rx.hstack(
                    rx.badge(
                        framework["scope"],
                        color_scheme="plum",
                        variant="soft",
                        size="1",
                    ),
                    rx.badge(
                        framework["complexity"],
                        color_scheme=rx.cond(
                            framework["complexity"] == "complex", "accent", "jade"
                        ),
                        variant="soft",
                        size="1",
                    ),
                    spacing="2",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.spacer(),
            rx.text(f"{framework['author']}", color="gray", size="2"),
            spacing="1",
            align="start",
            width="100%",
            justify="start",
            height="100%",
        ),
        width="100%",
        on_click=lambda: FrameworkState.show_framework_dialog(framework),
        style={
            "transition": "all 0.2s ease",
            "cursor": "pointer",
        },
        _hover={
            "transform": "translateY(-0.25em)",
            "boxShadow": "0 0.5em 1.5em rgba(0,0,0,0.1)",
        },
    )


def categories_sidebar():
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.text("Scope", size="4"),
                rx.cond(
                    FrameworkState.loading_scopes,
                    rx.center(rx.spinner(size="3"), height="6em"),
                    rx.vstack(
                        rx.foreach(FrameworkState.scopes, scope_button),
                        spacing="3",
                        width="100%",
                        align="stretch",
                    ),
                ),
                width="100%",
            ),
            spacing="4",
            width="100%",
            align="stretch",
        ),
        flex=1,
        padding="0.75em",
        min_width="15em",
    )
