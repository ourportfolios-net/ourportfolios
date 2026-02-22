import reflex as rx
from ...state.home_state import HomeState
from ...components.cards import glass_card
from ...styles import (
    glow_orb_style,
    icon_box_style,
    DECISION_HUB_HOVER,
    white,
    indigo,
)

_CARD_H = "72px"
_INDIGO_BG = indigo(0.1)
_INDIGO_BORDER = f"1px solid {indigo(0.3)}"


def _skel(width: str, height: str = "12px") -> rx.Component:
    return rx.box(
        width=width, height=height, border_radius="4px", background=white(0.08)
    )


def framework_skeleton_card(icon_name: str, index: int) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=18, color=white(0.3)),
                **icon_box_style("indigo", size="36px", radius="12px"),
                opacity=rx.cond(HomeState.framework_hover_index == index, "0", "1"),
                transition="opacity 0.3s ease",
            ),
            rx.vstack(
                _skel("100px", "13px"),
                _skel("100%", "24px"),
                spacing="2",
                align="start",
                flex="1",
                overflow="hidden",
                opacity=rx.cond(HomeState.framework_hover_index == index, "0", "1"),
                transition="opacity 0.3s ease",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.75rem",
        border_radius="10px",
        background=white(0.03),
        border=f"1px solid {white(0.05)}",
        width="100%",
        height=_CARD_H,
    )


def framework_glass_block(icon_name: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(icon_name, size=18, color="var(--indigo-9)"),
            **icon_box_style("indigo", size="36px", radius="12px"),
        ),
        rx.vstack(
            rx.text(
                title,
                font_size="13px",
                font_weight="700",
                color="white",
                line_height="1",
            ),
            rx.text(
                description,
                font_size="11px",
                color=white(0.6),
                line_height="1.4",
                margin_top="4px",
            ),
            spacing="1",
            align="start",
            flex="1",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.75rem",
    )


def select_framework_card() -> rx.Component:
    return rx.box(
        rx.box(**glow_orb_style("purple")),
        glass_card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Select Framework", size="5", font_weight="700"),
                        rx.text(
                            "Define your strategy. Choose from Growth, Value, or Dividend focused models.",
                            color=white(0.5),
                            font_size="12px",
                            line_height="1.5",
                        ),
                        spacing="2",
                        align="start",
                        flex="1",
                    ),
                    rx.box(
                        rx.icon("target", size=20, color="var(--accent-purple)"),
                        **icon_box_style("purple", radius="12px"),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.box(flex="1"),
                rx.box(
                    rx.vstack(
                        rx.vstack(
                            rx.box(
                                width="80px",
                                height="10px",
                                border_radius="4px",
                                background=white(0.08),
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                            margin_bottom="0.75rem",
                        ),
                        rx.box(
                            rx.vstack(
                                framework_skeleton_card(icon_name="shield", index=0),
                                framework_skeleton_card(icon_name="zap", index=1),
                                spacing="2",
                                align="start",
                                width="100%",
                            ),
                            rx.box(
                                rx.box(
                                    rx.box(
                                        framework_glass_block(
                                            "shield",
                                            "Value Investing",
                                            "Focuses on undervalued assets with strong fundamentals.",
                                        ),
                                        position="absolute",
                                        top="0",
                                        left="0",
                                        right="0",
                                        height=_CARD_H,
                                    ),
                                    rx.box(
                                        framework_glass_block(
                                            "zap",
                                            "Growth Strategy",
                                            "Targets high-growth companies with expanding market share.",
                                        ),
                                        position="absolute",
                                        top=f"calc({_CARD_H} + 8px)",
                                        left="0",
                                        right="0",
                                        height=_CARD_H,
                                    ),
                                    position="absolute",
                                    top=rx.cond(
                                        HomeState.framework_hover_index == 0,
                                        "0",
                                        f"calc(-{_CARD_H} - 8px)",
                                    ),
                                    left="0",
                                    right="0",
                                    height=f"calc({_CARD_H} * 2 + 8px)",
                                    transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                ),
                                position="absolute",
                                top=rx.cond(
                                    HomeState.framework_hover_index == 0,
                                    "0",
                                    f"calc({_CARD_H} + 8px)",
                                ),
                                left="0",
                                right="0",
                                height=_CARD_H,
                                background=f"linear-gradient(135deg, {_INDIGO_BG} 0%, {indigo(0.04)} 100%)",
                                backdrop_filter="blur(8px)",
                                border_radius="10px",
                                border=f"1.5px solid {indigo(0.4)}",
                                box_shadow=f"0 4px 20px {indigo(0.15)}, inset 0 1px 1px {white(0.1)}",
                                overflow="hidden",
                                transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                pointer_events="none",
                            ),
                            position="relative",
                            width="100%",
                            height=f"calc({_CARD_H} * 2 + 8px)",
                        ),
                        spacing="0",
                        align="start",
                        width="100%",
                    ),
                    **{
                        **{
                            k: v
                            for k, v in {
                                "padding": "0.75rem",
                                "border_radius": "10px",
                                "width": "100%",
                            }.items()
                        },
                        "background": white(0.03),
                        "border": f"1px solid {white(0.05)}",
                    },
                ),
                rx.button(
                    "Browse Frameworks",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="solid",
                    on_click=rx.redirect("/framework"),
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                width="100%",
                height="100%",
            ),
            padding="1rem",
            width="100%",
            height="420px",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        on_mouse_enter=HomeState.start_framework_hover,
        on_mouse_leave=HomeState.stop_framework_hover,
        **DECISION_HUB_HOVER,
    )
