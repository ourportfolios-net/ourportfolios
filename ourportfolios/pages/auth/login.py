"""Auth login and registration page."""

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.auth.components import (
    INPUT_OVERRIDE,
    action_btn,
    auth_card,
    auth_centered,
    auth_page_shell,
    divider_with_text,
    google_button,
    label,
    session_check_screen,
    text_input,
)
from ourportfolios.state.auth_state import AuthState
from ourportfolios.styles import (
    ERROR_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_TERTIARY,
    white,
)


def _inline_link(label_text: str, on_click: object) -> rx.Component:
    return rx.text(
        label_text,
        size="1",
        color=white(0.5),
        cursor="pointer",
        transition="color 0.15s ease, text-decoration 0.15s ease",
        _hover={"color": "white", "text_decoration": "underline"},
        on_click=on_click,
        display="inline",
    )


def _footer_row(prompt: str, link_text: str, on_click: object) -> rx.Component:
    return rx.hstack(
        rx.text(prompt, size="1", color=TEXT_MUTED),
        _inline_link(link_text, on_click),
        spacing="2",
        align="center",
        justify="center",
        width="100%",
    )


def _forgot_password_content() -> rx.Component:
    return rx.cond(
        AuthState.forgot_sent,
        rx.vstack(
            rx.hstack(
                rx.icon("circle-check", size=15, color=white(0.4)),
                rx.text("Reset link sent", size="2", weight="medium", color=white(0.6)),
                spacing="2",
                align="center",
                padding="0.6rem 0.875rem",
                background=white(0.04),
                border=f"1px solid {white(0.09)}",
                border_radius="0.625rem",
                width="100%",
                justify="center",
            ),
            rx.text(
                "Check your inbox — if that address is registered you'll get the link shortly.",
                size="1",
                color=white(0.35),
                line_height="1.65",
                text_align="center",
            ),
            action_btn(
                "Done",
                AuthState.close_forgot,
                loading=False,
                loading_label="",
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        rx.vstack(
            rx.text(
                "We'll send a reset link to your email address.",
                size="1",
                color=white(0.35),
                line_height="1.6",
            ),
            rx.vstack(
                label("Email"),
                text_input(
                    "you@example.com",
                    AuthState.forgot_email,
                    AuthState.set_forgot_email,
                    "email",
                ),
                spacing="0",
                width="100%",
                align="start",
            ),
            rx.cond(
                AuthState.forgot_error != "",
                rx.text(AuthState.forgot_error, size="1", color=ERROR_COLOR),
                rx.text(" ", size="1"),
            ),
            action_btn(
                "Send reset link",
                AuthState.handle_forgot_password,
                loading=AuthState.forgot_loading,
                loading_label="Sending…",
            ),
            spacing="3",
            width="100%",
        ),
    )


def _forgot_password_modal() -> rx.Component:
    return common_dialog(
        _forgot_password_content(),
        CommonDialogConfig(
            is_open=AuthState.forgot_open,
            on_close=AuthState.close_forgot,
            title="Reset password",
            width="22rem",
            height="auto",
            padding="1.5rem",
        ),
    )


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
        rx.vstack(
            label("Email"),
            text_input(
                "you@example.com",
                AuthState.email,
                AuthState.set_email,
                "email",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            rx.hstack(
                rx.text("Password", size="1", color=white(0.5), weight="medium"),
                rx.spacer(),
                _inline_link("Forgot password?", AuthState.open_forgot),
                width="100%",
                align="center",
                margin_bottom="0.4rem",
            ),
            rx.input(
                placeholder="••••••••",
                value=AuthState.password,
                on_change=AuthState.set_password,
                on_key_down=AuthState.handle_login_on_enter,
                type="password",
                style=INPUT_OVERRIDE,
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.cond(
            AuthState.error != "",
            rx.vstack(
                rx.text(AuthState.error, size="1", color=ERROR_COLOR),
                rx.cond(
                    AuthState.show_resend,
                    rx.text(
                        "Resend confirmation email",
                        size="1",
                        color=white(0.5),
                        text_decoration="underline",
                        cursor="pointer",
                        _hover={"color": "white"},
                        on_click=AuthState.resend_confirmation,
                    ),
                    rx.fragment(),
                ),
                spacing="1",
                align="start",
            ),
            rx.text(" ", size="1"),
        ),
        action_btn(
            "Sign in",
            AuthState.handle_login,
            loading=AuthState.loading,
            loading_label="Signing in…",
        ),
        divider_with_text("or"),
        google_button(),
        _footer_row(
            "Don't have an account?",
            "Create one",
            AuthState.set_mode_register,
        ),
        _footer_row(
            "Only trying things out?",
            "Be ourguest",
            AuthState.continue_as_guest,
        ),
        spacing="4",
        width="100%",
        align="start",
    )


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
            label("Full name"),
            text_input(
                "Your name",
                AuthState.full_name,
                AuthState.set_full_name,
                "text",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            label("Email"),
            text_input(
                "you@example.com",
                AuthState.email,
                AuthState.set_email,
                "email",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.hstack(
            rx.vstack(
                label("Password"),
                rx.input(
                    placeholder="Min. 8 chars",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    type="password",
                    style=INPUT_OVERRIDE,
                ),
                spacing="0",
                width="100%",
                align="start",
            ),
            rx.vstack(
                label("Confirm"),
                rx.input(
                    placeholder="Repeat",
                    value=AuthState.confirm_password,
                    on_change=AuthState.set_confirm_password,
                    on_key_down=AuthState.handle_register_on_enter,
                    type="password",
                    style=INPUT_OVERRIDE,
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
        action_btn(
            "Create account",
            AuthState.handle_register,
            loading=AuthState.loading,
            loading_label="Creating account…",
        ),
        divider_with_text("or"),
        google_button(),
        rx.text(
            "By creating an account you agree to our terms of service and privacy policy.",
            size="1",
            color=TEXT_MUTED,
            text_align="center",
            line_height="1.6",
        ),
        _footer_row("Already have an account?", "Sign in", AuthState.set_mode_login),
        spacing="4",
        width="100%",
        align="start",
    )


@rx.page(route="/auth", on_load=AuthState.check_existing_session)
def login() -> rx.Component:
    is_login = AuthState.auth_mode == "login"

    return rx.box(
        rx.cond(~AuthState.session_checked, session_check_screen(), rx.fragment()),
        rx.cond(
            AuthState.session_checked,
            auth_page_shell(
                _forgot_password_modal(),
                auth_centered(
                    auth_card(_register_form()),
                    opacity=rx.cond(is_login, "0", "1"),
                    pointer_events=rx.cond(is_login, "none", "auto"),
                    transition="opacity 0.15s ease",
                ),
                auth_centered(
                    auth_card(_login_form()),
                    opacity=rx.cond(is_login, "1", "0"),
                    pointer_events=rx.cond(is_login, "auto", "none"),
                    transition="opacity 0.15s ease",
                ),
            ),
            rx.fragment(),
        ),
        position="relative",
        min_height="100vh",
        width="100%",
    )
