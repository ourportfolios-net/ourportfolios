import reflex as rx
from ...state.home_state import HomeState
from ...state.framework_state import GlobalFrameworkState
from ...components.cards import glass_card
from ...styles import (
    HUB_CARD_STYLE,
    PREVIEW_BOX_STYLE,
    SKELETON_BG,
    white,
    purple,
    accent_btn,
    icon_box,
)

_CARD_H = "68px"
_PREVIEW_H = "200px"


def _skel(width: str, height: str = "11px") -> rx.Component:
    return rx.box(
        width=width, height=height, border_radius="4px", background=SKELETON_BG
    )


def _skeleton_row(icon_name: str, index: int) -> rx.Component:
    faded = rx.cond(HomeState.framework_hover_index == index, "0", "1")
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=15, color=white(0.2)),
                background=white(0.05),
                border=f"1px solid {white(0.06)}",
                border_radius="8px",
                padding="7px",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
                opacity=faded,
                transition="opacity 0.3s ease",
            ),
            rx.vstack(
                _skel("90px", "12px"),
                _skel("100%", "20px"),
                spacing="2",
                align="start",
                flex="1",
                overflow="hidden",
                opacity=faded,
                transition="opacity 0.3s ease",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.625rem 0.75rem",
        border_radius="9px",
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
        width="100%",
        height=_CARD_H,
    )


def _glass_row(icon_name: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(icon_name, size=15, color=white(0.55)),
            background=white(0.06),
            border=f"1px solid {white(0.08)}",
            border_radius="8px",
            padding="7px",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="white"),
            rx.text(description, size="1", color=white(0.4), line_height="1.4"),
            spacing="0",
            align="start",
            flex="1",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.625rem 0.75rem",
    )


def _framework_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            _skel("60px", "9px"),
            rx.box(
                rx.vstack(
                    _skeleton_row("shield", 0),
                    _skeleton_row("zap", 1),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                # Sliding highlight overlay
                rx.box(
                    rx.box(
                        rx.box(
                            _glass_row(
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
                            _glass_row(
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
                    background=white(0.05),
                    border_radius="9px",
                    border=f"1px solid {white(0.1)}",
                    overflow="hidden",
                    transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                    pointer_events="none",
                ),
                position="relative",
                width="100%",
                height=f"calc({_CARD_H} * 2 + 8px)",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        **PREVIEW_BOX_STYLE,
        height=_PREVIEW_H,
    )


# ── Select Framework (hub card) ───────────────────────────────────────────────


def select_framework_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Select Framework", size="4", weight="bold", color="white"),
                    rx.text(
                        "Define your strategy. Choose from Growth, Value, or Dividend focused models.",
                        size="2",
                        color=white(0.38),
                        line_height="1.65",
                        style={
                            "display": "-webkit-box",
                            "-webkit-line-clamp": "3",
                            "-webkit-box-orient": "vertical",
                            "overflow": "hidden",
                        },
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                ),
                icon_box("target", color="purple"),
                spacing="3",
                align="start",
                width="100%",
            ),
            _framework_preview(),
            rx.spacer(),
            accent_btn("Browse Frameworks", href="/framework"),
            spacing="4",
            width="100%",
            height="100%",
        ),
        # Full-card overlay — below button
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="0",
            cursor="pointer",
            on_click=rx.redirect("/framework"),
        ),
        **HUB_CARD_STYLE,
        on_mouse_enter=HomeState.start_framework_hover,
        on_mouse_leave=HomeState.stop_framework_hover,
    )


# ── Selected Framework (sidebar card) ────────────────────────────────────────


def selected_framework_card():
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework", size="1", weight="medium", color=white(0.35)
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
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            size="1",
                            weight="bold",
                            color=white(0.2),
                            letter_spacing="0.08em",
                        ),
                        rx.text(
                            rx.cond(
                                GlobalFrameworkState.selected_framework.get("author"),
                                GlobalFrameworkState.selected_framework.get(
                                    "author", ""
                                ),
                                "—",
                            ),
                            size="2",
                            weight="medium",
                            color=white(0.5),
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    accent_btn(
                        "Change", icon="refresh-cw", href="/framework", icon_left=True
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
        ),
        glass_card(
            rx.vstack(
                rx.text(
                    "Selected Framework", size="1", weight="medium", color=white(0.22)
                ),
                rx.vstack(
                    rx.text(
                        "No Framework Selected",
                        size="4",
                        weight="bold",
                        color=white(0.28),
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
                rx.spacer(),
                accent_btn("Select Framework", href="/framework"),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
        ),
    )
