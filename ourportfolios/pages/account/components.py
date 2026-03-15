"""Place at: ourportfolios/pages/account/components.py"""

import reflex as rx
from .state import AccountState, EXPERIENCE_OPTIONS
from ...state.auth_state import AuthState
from ...styles import (
    white,
    red,
    TEXT_PRIMARY,
    TEXT_TERTIARY,
    TEXT_MUTED,
    CARD_BG,
    CARD_BORDER,
    DIVIDER,
    MODAL_BG,
    INPUT_STYLE,
    LABEL_STYLE,
    ERROR_COLOR,
    BTN_GHOST_SM,
    icon_box,
)

# ─────────────────────────────────────────────────────────────────────────────
# One height for every interactive control — enforces visual consistency.
# ─────────────────────────────────────────────────────────────────────────────
_H = "2.25rem"

# _INPUT: INPUT_STYLE has background, border, border_radius, color, width,
#         _placeholder, _focus. We only add height and font_size — no overlap.
_INPUT = {**INPUT_STYLE, "height": _H, "font_size": "0.875rem", "width": "100%"}

# BTN_GHOST_SM has background, border, border_radius, color, cursor, _hover,
# transition. We only add on_click, padding, height, display, align_items,
# justify_content, flex_shrink — zero overlap.

_SUCCESS = "rgba(52,211,153,0.9)"


# ── Primitives ────────────────────────────────────────────────────────────────


def _divider() -> rx.Component:
    return rx.box(height="1px", background=DIVIDER, width="100%")


def _label(text: str) -> rx.Component:
    return rx.text(text, **LABEL_STYLE, margin_bottom="0.3rem")


def _btn(label: str, on_click, loading: bool = False) -> rx.Component:
    """Universal button — same height everywhere. Only safe keys after spread."""
    return rx.box(
        rx.cond(
            loading,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text("Saving…", size="1", color=TEXT_MUTED),
                spacing="2",
                align="center",
            ),
            rx.text(label, size="2", font_weight="500"),
        ),
        on_click=on_click,
        **BTN_GHOST_SM,
        padding="0 1rem",
        height=_H,
        display="inline-flex",
        align_items="center",
        justify_content="center",
        flex_shrink="0",
    )


def _feedback(msg, is_error: bool = False) -> rx.Component:
    color = ERROR_COLOR if is_error else _SUCCESS
    icon_name = "circle-alert" if is_error else "circle-check"
    return rx.hstack(
        rx.icon(icon_name, size=12, color=color),
        rx.text(msg, size="1", color=color),
        spacing="2",
        align="center",
    )


# ── Segmented control ────────────────────────────────────────────────────────
# Proper pill-style toggle. No dict spreads — all props explicit on rx.box.


def _segmented(options: list, active_var, on_change) -> rx.Component:
    def _seg_opt(label: str) -> rx.Component:
        is_active = active_var == label
        return rx.box(
            rx.text(
                label,
                size="2",
                font_weight=rx.cond(is_active, "500", "400"),
                color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED),
            ),
            on_click=on_change(label),
            height=_H,
            padding="0 0.875rem",
            display="inline-flex",
            align_items="center",
            justify_content="center",
            border_radius="0.375rem",
            background=rx.cond(is_active, white(0.08), "transparent"),
            border=rx.cond(
                is_active, f"1px solid {white(0.13)}", "1px solid transparent"
            ),
            cursor="pointer",
            transition="all 0.15s ease",
            _hover={"background": rx.cond(is_active, white(0.08), white(0.04))},
            flex="1",
        )

    return rx.hstack(
        *[_seg_opt(o) for o in options],
        spacing="0",
        gap="0.125rem",
        padding="0.1875rem",
        background=white(0.03),
        border=f"1px solid {white(0.07)}",
        border_radius="0.5rem",
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────


def _nav_item(tab: str, icon_name: str, label: str) -> rx.Component:
    is_active = AccountState.active_tab == tab
    return rx.box(
        rx.hstack(
            rx.icon(
                icon_name, size=14, color=rx.cond(is_active, white(0.75), white(0.28))
            ),
            rx.text(
                label, size="2", color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED)
            ),
            spacing="3",
            align="center",
        ),
        on_click=AccountState.set_active_tab(tab),
        padding="0.5rem 0.75rem",
        border_radius="0.5rem",
        background=rx.cond(is_active, white(0.05), "transparent"),
        border=rx.cond(is_active, f"1px solid {white(0.09)}", "1px solid transparent"),
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={"background": white(0.04)},
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        _nav_item("profile", "user", "Profile"),
        _nav_item("danger", "triangle-alert", "Danger zone"),
        spacing="1",
        width="10.5rem",
        flex_shrink="0",
        align="start",
    )


# ── Card primitives ───────────────────────────────────────────────────────────


def _card_header(icon_name: str, title: str, subtitle: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            icon_box(icon_name),
            rx.vstack(
                rx.text(
                    title,
                    size="3",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    letter_spacing="-0.01em",
                ),
                rx.text(subtitle, size="2", color=TEXT_TERTIARY),
                spacing="0",
            ),
            spacing="3",
            align="center",
        ),
        padding="1.25rem 1.5rem",
    )


def _row(title: str, desc: str, control: rx.Component) -> rx.Component:
    """Standard two-column row: label left, control right at fixed width."""
    return rx.hstack(
        rx.vstack(
            rx.text(title, size="2", weight="medium", color=TEXT_PRIMARY),
            rx.text(desc, size="1", color=TEXT_MUTED),
            spacing="0",
            align="start",
            flex="1",
        ),
        rx.box(control, width="13rem", flex_shrink="0"),
        align="center",
        width="100%",
        padding="1rem 1.5rem",
    )


# ── Password dialog ───────────────────────────────────────────────────────────


def _password_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.fragment()),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Change password",
                            size="4",
                            weight="bold",
                            color=TEXT_PRIMARY,
                            letter_spacing="-0.01em",
                        ),
                        rx.text(
                            "You'll be signed out after updating.",
                            size="2",
                            color=TEXT_TERTIARY,
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.box(
                        rx.icon("x", size=15, color=white(0.4)),
                        on_click=AccountState.close_password_dialog,
                        padding="0.25rem",
                        border_radius="0.375rem",
                        background="transparent",
                        border=f"1px solid transparent",
                        cursor="pointer",
                        transition="all 0.15s ease",
                        _hover={"background": white(0.08), "border_color": white(0.1)},
                        display="inline-flex",
                        align_items="center",
                        justify_content="center",
                        align_self="start",
                        flex_shrink="0",
                    ),
                    width="100%",
                    align="start",
                ),
                _divider(),
                rx.vstack(
                    rx.vstack(
                        _label("Current password"),
                        rx.input(
                            placeholder="Enter current password",
                            value=AccountState.old_password,
                            on_change=AccountState.set_old_password,
                            type="password",
                            **_INPUT,
                        ),
                        spacing="0",
                        width="100%",
                        align="start",
                    ),
                    rx.vstack(
                        _label("New password"),
                        rx.input(
                            placeholder="Min. 8 characters",
                            value=AccountState.new_password,
                            on_change=AccountState.set_new_password,
                            type="password",
                            **_INPUT,
                        ),
                        spacing="0",
                        width="100%",
                        align="start",
                    ),
                    rx.vstack(
                        _label("Confirm new password"),
                        rx.input(
                            placeholder="Repeat new password",
                            value=AccountState.confirm_password,
                            on_change=AccountState.set_confirm_password,
                            type="password",
                            **_INPUT,
                        ),
                        spacing="0",
                        width="100%",
                        align="start",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.cond(
                    AccountState.password_error != "",
                    _feedback(AccountState.password_error, is_error=True),
                    rx.fragment(),
                ),
                rx.hstack(
                    _btn("Cancel", on_click=AccountState.close_password_dialog),
                    _btn(
                        "Update password",
                        on_click=AccountState.save_password,
                        loading=AccountState.loading_password,
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                ),
                spacing="5",
                width="100%",
            ),
            background=MODAL_BG,
            border=CARD_BORDER,
            border_radius="0.875rem",
            padding="1.5rem",
            max_width="24rem",
            width="100%",
            box_shadow="0 2rem 5rem rgba(0,0,0,0.8)",
        ),
        open=AccountState.password_dialog_open,
        on_open_change=AccountState.set_password_dialog_open,
    )


# ── Panels ────────────────────────────────────────────────────────────────────


def profile_panel() -> rx.Component:
    # Password row: dots + Change button, together filling the control width
    pw_ctrl = rx.hstack(
        rx.text(
            "••••••••••", size="2", color=TEXT_MUTED, letter_spacing="0.1em", flex="1"
        ),
        _btn("Change", on_click=AccountState.open_password_dialog),
        align="center",
        width="100%",
    )

    return rx.box(
        _card_header("user", "Profile", "Manage your display name and preferences."),
        _divider(),
        _row(
            "Display name",
            "How you appear across the app.",
            rx.input(
                placeholder="Your name",
                value=AccountState.display_name,
                on_change=AccountState.set_display_name,
                **_INPUT,
            ),
        ),
        _divider(),
        _row(
            "Email address",
            "Used for sign-in and notifications.",
            rx.text(AuthState.user_email, size="2", color=TEXT_MUTED),
        ),
        _divider(),
        _row("Password", "Change your login credentials.", pw_ctrl),
        _divider(),
        _row(
            "Experience level",
            "Personalises your flow and features.",
            _segmented(
                EXPERIENCE_OPTIONS,
                AccountState.experience_level,
                AccountState.set_experience_level,
            ),
        ),
        _divider(),
        # Footer
        rx.box(
            rx.hstack(
                rx.cond(
                    AccountState.save_msg != "",
                    _feedback(AccountState.save_msg),
                    rx.cond(
                        AccountState.save_error != "",
                        _feedback(AccountState.save_error, is_error=True),
                        rx.cond(
                            AccountState.is_dirty,
                            rx.text("Unsaved changes", size="1", color=TEXT_MUTED),
                            rx.fragment(),
                        ),
                    ),
                ),
                rx.spacer(),
                _btn(
                    "Save changes",
                    on_click=AccountState.save_all,
                    loading=AccountState.loading_save,
                ),
                align="center",
                width="100%",
            ),
            padding="0.875rem 1.5rem",
        ),
        _password_dialog(),
        background=CARD_BG,
        border=CARD_BORDER,
        border_radius="0.875rem",
        width="100%",
        overflow="hidden",
    )


def danger_panel() -> rx.Component:
    return rx.box(
        _card_header(
            "triangle-alert", "Danger zone", "Irreversible and destructive actions."
        ),
        _divider(),
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Delete account", size="2", weight="medium", color=TEXT_PRIMARY
                    ),
                    rx.text(
                        "Permanently removes your account, portfolios, and all data.",
                        size="1",
                        color=TEXT_MUTED,
                    ),
                    spacing="1",
                    align="start",
                    flex="1",
                ),
                rx.box(
                    rx.text(
                        "Delete account", size="2", font_weight="500", color=red(0.8)
                    ),
                    padding="0 1rem",
                    height=_H,
                    background=red(0.05),
                    border=f"1px solid {red(0.14)}",
                    border_radius="0.4375rem",
                    cursor="pointer",
                    transition="all 0.15s ease",
                    _hover={"background": red(0.09), "border_color": red(0.25)},
                    display="inline-flex",
                    align_items="center",
                    flex_shrink="0",
                ),
                align="center",
                width="100%",
            ),
            padding="1rem 1.5rem",
        ),
        background=CARD_BG,
        border=f"1px solid {red(0.1)}",
        border_radius="0.875rem",
        width="100%",
        overflow="hidden",
    )


# ── Layout ────────────────────────────────────────────────────────────────────


def account_layout() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.cond(
                AccountState.active_tab == "profile", profile_panel(), rx.fragment()
            ),
            rx.cond(AccountState.active_tab == "danger", danger_panel(), rx.fragment()),
            flex="1",
            min_width="0",
        ),
        spacing="8",
        align="start",
        width="100%",
    )
