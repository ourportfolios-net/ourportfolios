import reflex as rx
from ...state.framework_state import GlobalFrameworkState
from ...components.cards import glass_card
from ...styles import white


def selected_framework_card():
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.icon("target", size=14, color=rx.color("purple", 9)),
                    rx.text(
                        "SELECTED FRAMEWORK",
                        font_size="10px",
                        font_weight="500",
                        letter_spacing="0.06em",
                        color=white(0.5),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.link(
                    rx.text(
                        GlobalFrameworkState.framework_display_name,
                        font_size="20px",
                        font_weight="700",
                        color="white",
                        line_height="1.2",
                    ),
                    href="/framework",
                    underline="none",
                ),
                rx.hstack(
                    rx.text(
                        rx.cond(
                            GlobalFrameworkState.selected_framework.get("author"),
                            f"by {GlobalFrameworkState.selected_framework.get('author', '')}",
                            "",
                        ),
                        font_size="11px",
                        font_weight="400",
                        color=white(0.4),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("refresh-cw", size=13),
                        "Change",
                        size="1",
                        on_click=rx.redirect("/framework"),
                        background=white(0.05),
                        border=f"1px solid {white(0.1)}",
                        border_radius="6px",
                        color=white(0.5),
                        cursor="pointer",
                        _hover={"background": white(0.09), "color": "white"},
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            transition="all 0.25s ease",
            _hover={"border_color": white(0.12)},
        ),
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.icon("target", size=14, color=white(0.2)),
                    rx.text(
                        "SELECTED FRAMEWORK",
                        font_size="10px",
                        font_weight="500",
                        letter_spacing="0.06em",
                        color=white(0.3),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    "No Framework Selected",
                    font_size="20px",
                    font_weight="700",
                    color=white(0.3),
                    line_height="1.2",
                ),
                rx.text(
                    "Choose a framework to guide your analysis",
                    font_size="11px",
                    font_weight="400",
                    color=white(0.25),
                    line_height="1.4",
                ),
                rx.button(
                    "Select Framework",
                    size="2",
                    variant="soft",
                    color_scheme="purple",
                    on_click=rx.redirect("/framework"),
                    width="100%",
                    margin_top="0.5rem",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            transition="all 0.25s ease",
            _hover={"border_color": white(0.08)},
        ),
    )
