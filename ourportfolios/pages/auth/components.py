"""Shared auth UI components."""

from typing import Literal

import reflex as rx

from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.theme.colors import TEXT_MUTED, TEXT_PRIMARY, purple, white
from ourportfolios.ui.theme.surfaces import (
    CARD_BG,
    CARD_BORDER,
    INPUT_STYLE,
    PAGE_BG,
    RADIUS_BUTTON,
    RADIUS_CARD,
)
from ourportfolios.ui.tokens import TRANS_DEFAULT

INPUT_OVERRIDE: dict[str, object] = {
    **INPUT_STYLE,
    "font_size": "0.9375rem",
    "height": "3rem",
    "padding": "0 0.9rem",
}


# ── Primitives ────────────────────────────────────────────────────────────────


def session_check_screen() -> rx.Component:
    return rx.box(
        rx.text(
            "ourportfolios",
            font_size="1.25rem",
            font_weight="600",
            letter_spacing="-0.02em",
            color=white(0.18),
            position="fixed",
            bottom="1.5rem",
            right="1.75rem",
            user_select="none",
        ),
        position="fixed",
        inset="0",
        background=PAGE_BG,
        z_index="9999",
        overflow="hidden",
    )


def label(text: str) -> rx.Component:
    return rx.box(
        rx.text(text, size="1", color=white(0.5), weight="medium"),
        margin_bottom="0.4rem",
    )


def text_input(
    placeholder: str,
    value: str | rx.Var[str],
    on_change: object,
    field_type: Literal["text", "email", "password"] = "text",
    *,
    auto_complete: str | None = None,
) -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        type=field_type,
        auto_complete=auto_complete,
        style=INPUT_OVERRIDE,
    )


_ACTION_BUTTON_STYLE = {
    "width": "100%",
    "height": "3rem",
    "background": white(0.08),
    "border": f"1px solid {white(0.14)}",
    "border_radius": RADIUS_BUTTON,
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.13), "border_color": white(0.22)},
}


def action_button(
    label_text: str,
    on_click: object,
    *,
    loading: bool | rx.Var[bool],
    loading_label: str,
) -> rx.Component:
    return rx.box(
        rx.cond(
            loading,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(loading_label, size="2", color=TEXT_MUTED),
                spacing="2",
                align="center",
            ),
            rx.text(label_text, size="2", weight="medium", color=TEXT_PRIMARY),
        ),
        on_click=on_click,
        display="flex",
        align_items="center",
        justify_content="center",
        style=_ACTION_BUTTON_STYLE,
    )


def divider_with_text(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(flex="1", height="1px", background=white(0.07)),
        rx.text(
            text,
            size="1",
            color=TEXT_MUTED,
            white_space="nowrap",
            padding_x="0.75rem",
        ),
        rx.box(flex="1", height="1px", background=white(0.07)),
        width="100%",
        align="center",
    )


_GOOGLE_BUTTON_STYLE = {
    "width": "100%",
    "height": "3rem",
    "background": white(0.04),
    "border": f"1px solid {white(0.1)}",
    "border_radius": RADIUS_BUTTON,
    "cursor": "pointer",
    "transition": TRANS_DEFAULT,
    "_hover": {"background": white(0.08), "border_color": white(0.18)},
}


def google_button() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.html(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="17" height="17">'
                '<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>'
                '<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>'
                '<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>'
                '<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>'
                "</svg>",
            ),
            rx.text(
                "Continue with Google",
                size="2",
                weight="medium",
                color=white(0.7),
            ),
            spacing="3",
            align="center",
            justify="center",
            width="100%",
        ),
        on_click=AuthState.handle_google_login,
        display="flex",
        align_items="center",
        justify_content="center",
        style=_GOOGLE_BUTTON_STYLE,
    )


def auth_card(*children: rx.Component) -> rx.Component:
    return rx.box(
        *children,
        background=CARD_BG,
        border=CARD_BORDER,
        border_radius=RADIUS_CARD,
        padding=rx.breakpoints(initial="1.25rem", sm="2rem"),
        width="100%",
        max_width=rx.breakpoints(initial="22rem", sm="28rem"),
        flex_shrink="0",
    )


# ── Shared layout pieces ──────────────────────────────────────────────────────


def auth_bg() -> rx.Component:
    """Purple glow orb — shared by all auth pages."""
    return rx.box(
        rx.box(
            position="absolute",
            top="-8rem",
            left="50%",
            transform="translateX(-50%)",
            width="50rem",
            height="32rem",
            background=f"radial-gradient(ellipse at 50% 0%, {purple(0.18)} 0%, transparent 65%)",
            pointer_events="none",
        ),
        position="absolute",
        inset="0",
        pointer_events="none",
        overflow="hidden",
        z_index="0",
    )


def auth_page_shell(*children: rx.Component) -> rx.Component:
    """Outer page wrapper — dark bg, centered content."""
    return rx.box(
        auth_bg(),
        *children,
        position="relative",
        background=PAGE_BG,
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
        overflow_y="auto",
    )


def auth_centered(
    *children: rx.Component,
    opacity: object | None = None,
    pointer_events: object | None = None,
    transition: object | None = None,
) -> rx.Component:
    """Centered card slot — flex-start align on mobile to allow scrolling."""
    return rx.box(
        *children,
        position="absolute",
        inset="0",
        display="flex",
        align_items="center",
        justify_content="center",
        padding=rx.breakpoints(initial="2rem 1rem 2rem", sm="0"),
        opacity=opacity,
        pointer_events=pointer_events,
        transition=transition,
    )
