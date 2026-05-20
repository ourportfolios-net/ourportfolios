"""Auth reset-password page."""

import reflex as rx

from ourportfolios.pages.auth.components import (
    INPUT_OVERRIDE,
    action_button,
    auth_card,
    auth_centered,
    auth_page_shell,
    label,
)
from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.primitives import body_text, heading, muted_text
from ourportfolios.ui.theme.colors import ERROR_COLOR, white
from ourportfolios.ui.theme.surfaces import RADIUS_INPUT


def _reset_form() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            heading("Set new password"),
            muted_text("Choose a new password for your account."),
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
                    body_text(
                        "Password updated",
                        weight="medium",
                        color=white(0.6),
                    ),
                    spacing="2",
                    align="center",
                    padding="0.6rem 0.875rem",
                    background=white(0.04),
                    border=f"1px solid {white(0.09)}",
                    border_radius=RADIUS_INPUT,
                    width="100%",
                    justify="center",
                ),
                muted_text(
                    "Your password has been updated. You can now sign in.",
                    text_align="center",
                ),
                action_button(
                    "Go to sign in",
                    rx.redirect("/auth"),
                    loading=False,
                    loading_label="",
                ),
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
                        style=INPUT_OVERRIDE,
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
                        style=INPUT_OVERRIDE,
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
                action_button(
                    "Update password",
                    AuthState.handle_reset_password,
                    loading=AuthState.reset_loading,
                    loading_label="Updating…",
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
