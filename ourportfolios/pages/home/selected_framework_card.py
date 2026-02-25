import reflex as rx
from ...state.framework_state import GlobalFrameworkState
from ...components.cards import glass_card
from ...styles import white, purple, TEXT_ACCENT


def selected_framework_card():
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework",
                    font_size="11px",
                    font_weight="500",
                    color=white(0.35),
                    letter_spacing="0.01em",
                ),
                rx.link(
                    rx.text(
                        GlobalFrameworkState.framework_display_name,
                        size="4",
                        weight="bold",
                        color="white",
                        line_height="1.35",
                    ),
                    href="/framework",
                    underline="none",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            font_size="9px",
                            font_weight="700",
                            letter_spacing="0.08em",
                            color=white(0.2),
                        ),
                        rx.text(
                            rx.cond(
                                GlobalFrameworkState.selected_framework.get("author"),
                                GlobalFrameworkState.selected_framework.get(
                                    "author", ""
                                ),
                                "—",
                            ),
                            font_size="12px",
                            font_weight="500",
                            color=white(0.5),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.hstack(
                            rx.text(
                                "CHANGE", size="1", weight="bold", color=TEXT_ACCENT
                            ),
                            rx.icon("arrow-right", size=12, color=TEXT_ACCENT),
                            spacing="1",
                            align="center",
                        ),
                        href="/framework",
                        underline="none",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
            transition="all 0.15s ease",
            _hover={"border_color": white(0.1), "background": white(0.03)},
        ),
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework",
                    font_size="11px",
                    font_weight="500",
                    color=white(0.22),
                    letter_spacing="0.01em",
                ),
                rx.vstack(
                    rx.text(
                        "No Framework Selected",
                        size="4",
                        weight="bold",
                        color=white(0.28),
                        line_height="1.3",
                    ),
                    rx.text(
                        "Choose a framework to guide your analysis",
                        size="2",
                        color=white(0.18),
                        line_height="1.6",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.box(
                    rx.link(
                        rx.hstack(
                            rx.text(
                                "Select Framework",
                                font_size="13px",
                                font_weight="700",
                                color=white(0.55),
                            ),
                            rx.icon("arrow-right", size=14, color=white(0.4)),
                            spacing="2",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        href="/framework",
                        underline="none",
                        width="100%",
                        display="flex",
                        justify_content="center",
                    ),
                    width="100%",
                    padding="0.6rem 1rem",
                    border_radius="9px",
                    background=white(0.03),
                    border=f"1px solid {white(0.07)}",
                    cursor="pointer",
                    transition="all 0.15s ease",
                    _hover={"background": white(0.06), "border_color": white(0.12)},
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
            transition="all 0.15s ease",
            _hover={"border_color": white(0.08)},
        ),
    )
