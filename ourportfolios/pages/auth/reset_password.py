"""Place at: ourportfolios/pages/auth/reset_password.py"""

import reflex as rx
from ...state.auth_state import AuthState
from ...styles import white, TEXT_PRIMARY, TEXT_TERTIARY, ERROR_COLOR
from .components import (
    label,
    action_btn,
    auth_card,
    auth_page_shell,
    auth_centered,
    INPUT_OVERRIDE,
)


def _reset_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Set new password",
                font_size="1.625rem",
                weight="bold",
                color=TEXT_PRIMARY,
                letter_spacing="-0.025em",
            ),
            rx.text(
                "Choose a new password for your account.",
                size="2",
                color=TEXT_TERTIARY,
                line_height="1.6",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.box(height="0.25rem"),
        rx.cond(
            AuthState.reset_done,
            rx.vstack(
                rx.hstack(
                    rx.icon("circle-check", size=15, color=white(0.4)),
                    rx.text(
                        "Password updated",
                        size="2",
                        weight="medium",
                        color=white(0.6),
                    ),
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
                    "Your password has been updated. You can now sign in.",
                    size="1",
                    color=white(0.35),
                    line_height="1.65",
                    text_align="center",
                ),
                action_btn("Go to sign in", rx.redirect("/auth"), False, ""),
                spacing="3",
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.vstack(
                    label("New password"),
                    rx.input(
                        placeholder="Min. 8 chars",
                        value=AuthState.reset_new_password,
                        on_change=AuthState.set_reset_new_password,
                        type="password",
                        auto_complete=False,
                        **INPUT_OVERRIDE,
                    ),
                    spacing="0",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    label("Confirm password"),
                    rx.input(
                        placeholder="Repeat",
                        value=AuthState.reset_confirm_password,
                        on_change=AuthState.set_reset_confirm_password,
                        type="password",
                        auto_complete=False,
                        **INPUT_OVERRIDE,
                    ),
                    spacing="0",
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    AuthState.reset_error != "",
                    rx.text(AuthState.reset_error, size="1", color=ERROR_COLOR),
                    rx.text(" ", size="1"),
                ),
                action_btn(
                    "Update password",
                    AuthState.handle_reset_password,
                    AuthState.reset_loading,
                    "Updating…",
                ),
                spacing="4",
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
        align="start",
    )


@rx.page(route="/auth/reset-password")
def reset_password() -> rx.Component:
    return auth_page_shell(
        auth_centered(auth_card(_reset_form())),
    )
