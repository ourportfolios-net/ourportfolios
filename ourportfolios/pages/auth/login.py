"""Place at: ourportfolios/pages/auth/login.py"""

import reflex as rx
from ...state.auth_state import AuthState
from ...styles import (
    white,
    purple,
    TEXT_PRIMARY,
    TEXT_TERTIARY,
    TEXT_MUTED,
    ERROR_COLOR,
    overlay_style,
)
from .components import _label, _input, _divider_with_text, _google_button, auth_card

_LINK = {"transition": "color 0.15s ease", "text_decoration_color": "inherit"}

# ── Session check screen ──────────────────────────────────────────────────────


def session_check_screen() -> rx.Component:
    return rx.box(
        rx.text(
            "ourportfolios",
            font_size="1rem",
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
        background="#090909",
        z_index="9999",
        overflow="hidden",
    )


# ── Link primitives ───────────────────────────────────────────────────────────


def _inline_link(label: str, on_click) -> rx.Component:
    return rx.text(
        label,
        size="1",
        color=white(0.5),
        text_decoration="underline",
        cursor="pointer",
        transition="color 0.15s ease",
        _hover={"color": "white"},
        on_click=on_click,
        display="inline",
    )


def _plain_link(label: str, href: str) -> rx.Component:
    return rx.link(
        label,
        href=href,
        size="1",
        color=white(0.5),
        text_decoration="underline",
        transition="color 0.15s ease",
        _hover={"color": "white"},
    )


def _action_btn(label: str, on_click, loading, loading_label: str) -> rx.Component:
    return rx.box(
        rx.cond(
            loading,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(loading_label, size="2", color=TEXT_MUTED),
                spacing="2",
                align="center",
            ),
            rx.text(label, size="2", weight="medium", color=TEXT_PRIMARY),
        ),
        width="100%",
        height="3rem",
        background=white(0.08),
        border=f"1px solid {white(0.14)}",
        border_radius="0.625rem",
        cursor="pointer",
        transition="background 0.15s, border-color 0.15s",
        _hover={"background": white(0.13), "border_color": white(0.22)},
        on_click=on_click,
        display="flex",
        align_items="center",
        justify_content="center",
    )


# ── Spacer keeps both forms the same height ───────────────────────────────────
# Login has fewer fields than register. We pad login at the bottom so the card
# never changes height when toggling modes.
_FORM_SPACER = rx.fragment()  # removed — same width is enough, no height padding needed


# ── Login form ────────────────────────────────────────────────────────────────


def _login_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Welcome back",
                font_size="1.625rem",
                weight="bold",
                color=TEXT_PRIMARY,
                letter_spacing="-0.025em",
            ),
            rx.text(
                "Sign in to your account to continue.",
                size="2",
                color=TEXT_TERTIARY,
                line_height="1.6",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.box(height="0.25rem"),
        # Spacer replaces the full-name field present in register
        _FORM_SPACER,
        rx.vstack(
            _label("Email"),
            _input("you@example.com", AuthState.email, AuthState.set_email, "email"),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(
                    "PASSWORD",
                    font_size="0.625rem",
                    font_weight="700",
                    color=white(0.35),
                    letter_spacing="0.08em",
                ),
                rx.spacer(),
                _plain_link("Forgot password?", "#"),
                width="100%",
                align="center",
                margin_bottom="0.4rem",
            ),
            _input("••••••••", AuthState.password, AuthState.set_password, "password"),
            spacing="0",
            width="100%",
            align="start",
        ),
        # Error OR empty hint line — keeps height stable
        rx.cond(
            AuthState.error != "",
            rx.text(AuthState.error, size="1", color=ERROR_COLOR),
            rx.text(" ", size="1"),  # invisible placeholder
        ),
        _action_btn(
            "Sign in", AuthState.handle_login, AuthState.loading, "Signing in…"
        ),
        _divider_with_text("or"),
        _google_button(),
        rx.hstack(
            rx.text("Don't have an account?", size="1", color=TEXT_MUTED),
            _inline_link("Create one", AuthState.set_mode_register),
            spacing="2",
            align="center",
            justify="center",
            width="100%",
        ),
        spacing="4",
        width="100%",
        align="start",
    )


# ── Register form ─────────────────────────────────────────────────────────────


def _register_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Create an account",
                font_size="1.625rem",
                weight="bold",
                color=TEXT_PRIMARY,
                letter_spacing="-0.025em",
            ),
            rx.text(
                "Start building your portfolio today.",
                size="2",
                color=TEXT_TERTIARY,
                line_height="1.6",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.box(height="0.25rem"),
        rx.vstack(
            _label("Full name"),
            _input("Your name", AuthState.full_name, AuthState.set_full_name),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            _label("Email"),
            _input("you@example.com", AuthState.email, AuthState.set_email, "email"),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.hstack(
            rx.vstack(
                _label("Password"),
                _input(
                    "Min. 8 chars",
                    AuthState.password,
                    AuthState.set_password,
                    "password",
                ),
                spacing="0",
                width="100%",
                align="start",
            ),
            rx.vstack(
                _label("Confirm"),
                _input(
                    "Repeat",
                    AuthState.confirm_password,
                    AuthState.set_confirm_password,
                    "password",
                ),
                spacing="0",
                width="100%",
                align="start",
            ),
            spacing="3",
            width="100%",
        ),
        rx.cond(
            AuthState.error != "",
            rx.text(AuthState.error, size="1", color=ERROR_COLOR),
            rx.text("At least 8 characters.", size="1", color=TEXT_MUTED),
        ),
        _action_btn(
            "Create account",
            AuthState.handle_register,
            AuthState.loading,
            "Creating account…",
        ),
        _divider_with_text("or"),
        _google_button(),
        rx.text(
            "By creating an account you agree to our terms of service and privacy policy.",
            size="1",
            color=TEXT_MUTED,
            text_align="center",
            line_height="1.6",
        ),
        rx.hstack(
            rx.text("Already have an account?", size="1", color=TEXT_MUTED),
            _inline_link("Sign in", AuthState.set_mode_login),
            spacing="2",
            align="center",
            justify="center",
            width="100%",
        ),
        spacing="4",
        width="100%",
        align="start",
    )


# ── Guest card — fixed position, right side ───────────────────────────────────


def _guest_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon("user-x", size=18, color=white(0.35)),
                padding="0.55rem",
                background=white(0.05),
                border=f"1px solid {white(0.1)}",
                border_radius="0.5rem",
                display="inline-flex",
            ),
            rx.vstack(
                rx.text("Guest access", size="2", weight="medium", color=white(0.5)),
                rx.text(
                    "No saved data, no frameworks, no history. You'll lose everything when you close the tab.",
                    size="1",
                    color=white(0.32),
                    line_height="1.7",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.box(
                rx.hstack(
                    rx.text(
                        "Be ourguest!", size="1", weight="medium", color=white(0.6)
                    ),
                    rx.icon("arrow-right", size=12, color=white(0.4)),
                    spacing="1",
                    align="center",
                ),
                padding="0.4rem 0.9rem",
                background=white(0.04),
                border=f"1px solid {white(0.09)}",
                border_radius="0.5rem",
                display="inline-flex",
                align_self="flex-end",
                position="relative",
                z_index="2",
                cursor="pointer",
                transition="background 0.15s, border-color 0.15s",
                _hover={"background": white(0.09), "border_color": white(0.22)},
                on_click=AuthState.continue_as_guest,
            ),
            spacing="4",
            align="start",
            width="100%",
            height="100%",
        ),
        # Full-card click overlay — same pattern as select_framework_card
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="1",
            cursor="pointer",
            on_click=AuthState.continue_as_guest,
        ),
        position="fixed",
        top="50%",
        left="calc(50% + 17rem)",
        transform="translateY(-50%)",
        background=white(0.04),
        border=f"1px solid {white(0.1)}",
        border_radius="1rem",
        padding="1.5rem",
        width="14rem",
        height="18rem",
        z_index="10",
        cursor="pointer",
        transition="background 0.15s, border-color 0.15s",
        _hover={"background": white(0.07), "border_color": white(0.18)},
        overflow="hidden",
    )


# ── Background ────────────────────────────────────────────────────────────────


def _bg() -> rx.Component:
    return rx.box(
        # Top-center purple glow
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


# ── Page ──────────────────────────────────────────────────────────────────────


@rx.page(route="/auth", on_load=AuthState.check_existing_session)
@rx.page(route="/login", on_load=AuthState.check_existing_session)
@rx.page(route="/register", on_load=AuthState.check_existing_session)
def login() -> rx.Component:
    is_login = AuthState.auth_mode == "login"

    # Both full cards in the DOM — the whole card slides + fades in/out.
    # Register card sits in normal flow to anchor the center container height.
    # Login card is absolute on top.
    return rx.box(
        rx.cond(~AuthState.session_checked, session_check_screen(), rx.fragment()),
        rx.cond(
            AuthState.session_checked,
            rx.box(
                _bg(),
                _guest_card(),
                # Register card layer — centers itself in the viewport
                rx.box(
                    auth_card(_register_form()),
                    position="absolute",
                    inset="0",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    opacity=rx.cond(is_login, "0", "1"),
                    pointer_events=rx.cond(is_login, "none", "auto"),
                    transition="opacity 0.15s ease",
                ),
                # Login card layer — centers itself in the viewport
                rx.box(
                    auth_card(_login_form()),
                    position="absolute",
                    inset="0",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    opacity=rx.cond(is_login, "1", "0"),
                    pointer_events=rx.cond(is_login, "auto", "none"),
                    transition="opacity 0.15s ease",
                ),
                position="relative",
                min_height="100vh",
            ),
            rx.fragment(),
        ),
        position="relative",
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
