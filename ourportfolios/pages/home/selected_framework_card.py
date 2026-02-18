import reflex as rx
from ...state.framework_state import GlobalFrameworkState
from ...components.cards import glass_card


def selected_framework_card():
    """Card showing the currently selected framework."""
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        # Framework is selected
        glass_card(
            rx.link(
                rx.box(
                    height="100%",
                    width="100%",
                    position="absolute",
                    top="0",
                    left="0",
                    z_index="1",
                ),
                href="/framework",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "target",
                        size=14,
                        color=rx.color("purple", 9),
                    ),
                    rx.text(
                        "SELECTED FRAMEWORK",
                        font_size="10px",
                        font_weight="500",
                        letter_spacing="0.06em",
                        color="rgba(255, 255, 255, 0.5)",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    GlobalFrameworkState.framework_display_name,
                    font_size="20px",
                    font_weight="700",
                    color="white",
                    line_height="1.2",
                ),
                # Author and Change button on the same row
                rx.hstack(
                    rx.text(
                        rx.cond(
                            GlobalFrameworkState.selected_framework.get("author"),
                            f"by {GlobalFrameworkState.selected_framework.get('author', '')}",
                            "",
                        ),
                        font_size="11px",
                        font_weight="400",
                        color="rgba(255, 255, 255, 0.4)",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("refresh-cw", size=13),
                        "Change",
                        size="1",
                        on_click=rx.redirect("/framework"),
                        position="relative",
                        z_index="10",
                        style={
                            "background": "rgba(255,255,255,0.05)",
                            "border": "1px solid rgba(255,255,255,0.1)",
                            "border_radius": "6px",
                            "color": "rgba(255,255,255,0.5)",
                            "cursor": "pointer",
                            "_hover": {
                                "background": "rgba(255,255,255,0.09)",
                                "color": "white",
                            },
                        },
                    ),
                    width="100%",
                    align="center",
                    pointer_events="auto",
                ),
                spacing="3",
                align="start",
                width="100%",
                position="relative",
                z_index="2",
                pointer_events="none",
                style={"& button": {"pointer-events": "auto"}},
            ),
            padding="1rem",
            width="100%",
            transition="all 0.25s ease",
            position="relative",
            _hover={
                "border_color": "rgba(255, 255, 255, 0.12)",
            },
        ),
        # No framework selected
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "target",
                        size=14,
                        color="rgba(255, 255, 255, 0.2)",
                    ),
                    rx.text(
                        "SELECTED FRAMEWORK",
                        font_size="10px",
                        font_weight="500",
                        letter_spacing="0.06em",
                        color="rgba(255, 255, 255, 0.3)",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    "No Framework Selected",
                    font_size="20px",
                    font_weight="700",
                    color="rgba(255, 255, 255, 0.3)",
                    line_height="1.2",
                ),
                rx.text(
                    "Choose a framework to guide your analysis",
                    font_size="11px",
                    font_weight="400",
                    color="rgba(255, 255, 255, 0.25)",
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
            _hover={
                "border_color": "rgba(255, 255, 255, 0.08)",
            },
        ),
    )
