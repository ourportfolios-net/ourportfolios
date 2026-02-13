"""Framework recommendation page - select investment frameworks."""

import reflex as rx

from ...components.navbar import navbar
from ...components.page_roller import card_roller, card_link

from .state import FrameworkState
from .framework_cards import categories_sidebar, framework_card
from .framework_dialog import framework_dialog
from .add_framework_dialog import add_framework_dialog, add_metric_selector


def page_selection():
    return rx.box(
        card_roller(
            card_link(
                rx.hstack(
                    rx.icon("chevron_left", size=32),
                    rx.vstack(
                        rx.heading("Ourportfolios", weight="regular", size="5"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    align="center",
                    justify="center",
                ),
                href="/",
            ),
            card_link(
                rx.vstack(
                    rx.heading("Recommend", weight="regular", size="7"),
                    rx.text("Framework Selection", size="3"),
                    align="center",
                    justify="center",
                    height="100%",
                    spacing="1",
                ),
                href="/recommend",
            ),
            card_link(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Select", weight="regular", size="5"),
                        rx.text("caijdo", size="1"),
                        align="center",
                        justify="center",
                        height="100%",
                        spacing="1",
                    ),
                    rx.icon("chevron_right", size=32),
                    align="center",
                    justify="center",
                ),
                href="/select",
            ),
        ),
        width="100%",
        display="flex",
        justify_content="center",
        align_items="center",
        margin="0",
        padding="0",
    )


def frameworks_content():
    return rx.fragment(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Frameworks", size="4"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("plus", size=18),
                        "Add Framework",
                        on_click=FrameworkState.open_add_dialog,
                        size="2",
                        variant="soft",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.cond(
                    FrameworkState.loading_frameworks,
                    rx.center(rx.spinner(size="3"), height="12em"),
                    rx.cond(
                        FrameworkState.frameworks.length() > 0,
                        rx.vstack(
                            rx.foreach(FrameworkState.frameworks, framework_card),
                            spacing="3",
                            width="100%",
                            padding="0.5em",
                        ),
                        rx.center(
                            rx.text(
                                "No frameworks in this category yet.",
                                color="gray",
                                size="3",
                            ),
                            height="12em",
                        ),
                    ),
                ),
                spacing="2",
                width="100%",
                align="stretch",
            ),
            flex=4,
            min_width=0,
            max_width="100%",
            padding="0.75em",
        ),
        framework_dialog(),
        add_framework_dialog(),
        add_metric_selector(),
    )


@rx.page(route="/recommend", on_load=[FrameworkState.on_mount])
def index() -> rx.Component:
    return rx.box(
        rx.fragment(
            navbar(),
            page_selection(),
            rx.center(
                rx.box(
                    rx.hstack(
                        categories_sidebar(),
                        frameworks_content(),
                        spacing="3",
                        width="100%",
                    ),
                    width="86vw",
                ),
                width="100%",
                padding="2rem",
                padding_top="5rem",
                position="relative",
            ),
        ),
        on_unmount=FrameworkState.on_unmount,
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
