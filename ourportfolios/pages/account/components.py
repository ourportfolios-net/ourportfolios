"""Place at: ourportfolios/pages/account/components.py"""

import reflex as rx
from .state import AccountState, EXPERIENCE_OPTIONS, DEFAULT_PERIOD_OPTIONS
from ...state.auth_state import AuthState
from ...components.common_dialog import common_dialog
from ...styles import (
    white,
    red,
    purple,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    TEXT_MUTED,
    CARD_BG,
    CARD_BORDER,
    DIVIDER,
    INPUT_STYLE,
    LABEL_STYLE,
    ERROR_COLOR,
    BTN_GHOST_SM,
    icon_box,
)

# ── Tokens ────────────────────────────────────────────────────────────────────

_H = "2.125rem"
_SUCCESS = "rgba(52,211,153,0.9)"

_INPUT = {**INPUT_STYLE, "height": _H, "font_size": "0.875rem", "width": "100%"}
_INPUT_DLG = {
    **INPUT_STYLE,
    "height": "2.625rem",
    "font_size": "0.9375rem",
    "width": "100%",
}

_BTN = {
    **BTN_GHOST_SM,
    "height": _H,
    "padding": "0 0.875rem",
    "display": "inline-flex",
    "align_items": "center",
    "justify_content": "center",
    "flex_shrink": "0",
    "font_size": "0.8125rem",
    "font_weight": "500",
}

# ── Primitives ────────────────────────────────────────────────────────────────


def _divider() -> rx.Component:
    return rx.box(height="1px", background=DIVIDER, width="100%")


def _label(text: str) -> rx.Component:
    return rx.text(text, **LABEL_STYLE)


def _ghost_btn(label: str, on_click) -> rx.Component:
    return rx.box(
        rx.text(label, size="2", font_weight="500"), on_click=on_click, **_BTN
    )


def _loading_btn(label: str, on_click, loading_var) -> rx.Component:
    return rx.box(
        rx.cond(
            loading_var,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text("Saving…", size="2", color=TEXT_MUTED),
                spacing="2",
                align="center",
            ),
            rx.text(label, size="2", font_weight="500"),
        ),
        on_click=on_click,
        **_BTN,
    )


def _feedback(msg, is_error: bool = False) -> rx.Component:
    color = ERROR_COLOR if is_error else _SUCCESS
    return rx.hstack(
        rx.icon("circle-alert" if is_error else "circle-check", size=12, color=color),
        rx.text(msg, size="2", color=color),
        spacing="2",
        align="center",
    )


# ── Dialog header (title + X, no extra row wasted) ────────────────────────────
# We always use show_close_button=False in common_dialog and build the header
# ourselves so title and X live in the same hstack — zero wasted vertical space.


def _dlg_header(title: str, subtitle: str, on_close) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(
                title,
                size="4",
                weight="bold",
                color=TEXT_PRIMARY,
                letter_spacing="-0.02em",
            ),
            rx.text(subtitle, size="2", color=TEXT_TERTIARY),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.dialog.close(
            rx.box(
                rx.icon("x", size=15, color=white(0.35)),
                on_click=on_close,
                padding="0.3rem",
                border_radius="0.375rem",
                background="transparent",
                border="1px solid transparent",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": white(0.07), "border_color": white(0.1)},
                display="inline-flex",
                align_items="center",
                justify_content="center",
                align_self="start",
                flex_shrink="0",
            ),
        ),
        align="start",
        width="100%",
    )


# ── Card shell ────────────────────────────────────────────────────────────────


def _card(*children, border: str = CARD_BORDER) -> rx.Component:
    return rx.box(
        *children,
        background=CARD_BG,
        border=border,
        border_radius="0.875rem",
        width="100%",
        overflow="hidden",
    )


def _card_header(
    icon_name: str, title: str, subtitle: str, color: str = "purple"
) -> rx.Component:
    return rx.hstack(
        icon_box(icon_name, color=color),
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
        padding="1.25rem 1.5rem",
        width="100%",
    )


# ── Password dialog ───────────────────────────────────────────────────────────


def _password_dialog() -> rx.Component:
    content = rx.vstack(
        _dlg_header(
            "Change password",
            "You'll be signed out on all devices after updating.",
            AccountState.close_password_dialog,
        ),
        _divider(),
        # Current password — visually separated from new ones
        rx.vstack(
            _label("Current password"),
            rx.input(
                placeholder="Enter your current password",
                value=AccountState.old_password,
                on_change=AccountState.set_old_password,
                type="password",
                **_INPUT_DLG,
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
        # New + Confirm as a visual group
        rx.vstack(
            rx.vstack(
                _label("New password"),
                rx.input(
                    placeholder="At least 8 characters",
                    value=AccountState.new_password,
                    on_change=AccountState.set_new_password,
                    type="password",
                    **_INPUT_DLG,
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            rx.vstack(
                _label("Confirm new password"),
                rx.input(
                    placeholder="Repeat your new password",
                    value=AccountState.confirm_password,
                    on_change=AccountState.set_confirm_password,
                    type="password",
                    **_INPUT_DLG,
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            spacing="3",
            width="100%",
        ),
        rx.cond(
            AccountState.password_error != "",
            _feedback(AccountState.password_error, is_error=True),
            rx.fragment(),
        ),
        _divider(),
        rx.hstack(
            _ghost_btn("Cancel", on_click=AccountState.close_password_dialog),
            _loading_btn(
                "Update password",
                on_click=AccountState.save_password,
                loading_var=AccountState.loading_password,
            ),
            spacing="2",
            justify="end",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

    return common_dialog(
        content=content,
        is_open=AccountState.password_dialog_open,
        on_close=AccountState.close_password_dialog,
        on_open_change=AccountState.set_password_dialog_open,
        show_close_button=False,
        width="90vw",
        max_width="27rem",
        height="fit-content",
        padding="1.5rem",
    )


# ── Delete dialog ─────────────────────────────────────────────────────────────


def _delete_dialog() -> rx.Component:
    content = rx.vstack(
        _dlg_header(
            "Delete your account",
            "This permanently removes all your data. There is no way to undo this.",
            AccountState.close_delete_dialog,
        ),
        _divider(),
        rx.vstack(
            rx.hstack(
                rx.text("Type", size="2", color=TEXT_MUTED),
                rx.text(
                    "DELETE",
                    size="2",
                    font_weight="700",
                    color=red(0.7),
                    font_family="monospace",
                    letter_spacing="0.06em",
                ),
                rx.text("to confirm.", size="2", color=TEXT_MUTED),
                spacing="1",
                align="center",
            ),
            rx.input(
                placeholder="DELETE",
                value=AccountState.delete_confirm_text,
                on_change=AccountState.set_delete_confirm_text,
                **_INPUT_DLG,
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
        rx.cond(
            AccountState.delete_error != "",
            _feedback(AccountState.delete_error, is_error=True),
            rx.fragment(),
        ),
        _divider(),
        rx.hstack(
            _ghost_btn("Cancel", on_click=AccountState.close_delete_dialog),
            rx.box(
                rx.cond(
                    AccountState.loading_delete,
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Deleting…", size="2", color=red(0.6)),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Delete account", size="2", font_weight="500", color=red(0.8)
                    ),
                ),
                on_click=AccountState.confirm_delete_account,
                height=_H,
                padding="0 0.875rem",
                background=red(0.07),
                border=f"1px solid {red(0.18)}",
                border_radius="0.4375rem",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": red(0.12), "border_color": red(0.3)},
                display="inline-flex",
                align_items="center",
                flex_shrink="0",
            ),
            spacing="2",
            justify="end",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )

    return common_dialog(
        content=content,
        is_open=AccountState.delete_dialog_open,
        on_close=AccountState.close_delete_dialog,
        on_open_change=AccountState.set_delete_dialog_open,
        show_close_button=False,
        width="90vw",
        max_width="27rem",
        height="fit-content",
        padding="1.5rem",
    )


# ── Profile card ──────────────────────────────────────────────────────────────
# Layout:
#   [header]
#   ─────────
#   Display name label + full-width input
#   Email   ·   password dots + Change →       ← secondary, one row
#   ─────────
#   [feedback]  [Save changes]


def profile_panel() -> rx.Component:
    return _card(
        _card_header("user", "Profile", "Manage your display name and credentials."),
        _divider(),
        rx.box(
            rx.vstack(
                # Primary: display name
                rx.vstack(
                    _label("Display name"),
                    rx.input(
                        placeholder="Your name",
                        value=AccountState.display_name,
                        on_change=AccountState.set_display_name,
                        **_INPUT,
                    ),
                    spacing="2",
                    width="100%",
                    align="start",
                ),
                # Secondary row: email left, password right
                rx.hstack(
                    # Email
                    rx.hstack(
                        rx.icon("mail", size=13, color=white(0.2)),
                        rx.text(AuthState.user_email, size="2", color=TEXT_MUTED),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    # Password
                    rx.hstack(
                        rx.text(
                            "••••••••",
                            size="2",
                            color=TEXT_MUTED,
                            letter_spacing="0.08em",
                        ),
                        rx.box(
                            rx.text(
                                "Change →",
                                size="2",
                                color=white(0.28),
                                cursor="pointer",
                                transition="color 0.15s ease",
                                _hover={"color": white(0.6)},
                            ),
                            on_click=AccountState.open_password_dialog,
                        ),
                        spacing="3",
                        align="center",
                    ),
                    align="center",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            padding="1.25rem 1.5rem",
        ),
        _divider(),
        rx.hstack(
            rx.cond(
                AccountState.save_msg != "",
                _feedback(AccountState.save_msg),
                rx.cond(
                    AccountState.save_error != "",
                    _feedback(AccountState.save_error, is_error=True),
                    rx.cond(
                        AccountState.profile_dirty,
                        rx.text("Unsaved changes", size="2", color=TEXT_MUTED),
                        rx.fragment(),
                    ),
                ),
            ),
            rx.spacer(),
            _loading_btn(
                "Save changes",
                on_click=AccountState.save_all,
                loading_var=AccountState.loading_save,
            ),
            align="center",
            width="100%",
            padding="0.875rem 1.5rem",
        ),
        _password_dialog(),
    )


# ── Delete card ───────────────────────────────────────────────────────────────


def delete_card() -> rx.Component:
    return _card(
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Delete account", size="2", weight="medium", color=TEXT_PRIMARY
                ),
                rx.text(
                    "Permanently removes your account and all associated data.",
                    size="2",
                    color=TEXT_MUTED,
                ),
                spacing="1",
                align="start",
                flex="1",
            ),
            rx.box(
                rx.text("Delete account", size="2", font_weight="500", color=red(0.75)),
                on_click=AccountState.open_delete_dialog,
                height=_H,
                padding="0 0.875rem",
                background=red(0.05),
                border=f"1px solid {red(0.14)}",
                border_radius="0.4375rem",
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": red(0.1), "border_color": red(0.26)},
                display="inline-flex",
                align_items="center",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding="1.125rem 1.5rem",
        ),
        _delete_dialog(),
        border=f"1px solid {red(0.1)}",
    )


# ── Experience cards ──────────────────────────────────────────────────────────


def _exp_card(label: str, description: str) -> rx.Component:
    is_active = AccountState.experience_level == label
    return rx.box(
        # Tick — top right, only when active
        rx.cond(
            is_active,
            rx.box(
                rx.icon("check", size=11, color=purple(0.95)),
                position="absolute",
                top="0.75rem",
                right="0.75rem",
                width="1.375rem",
                height="1.375rem",
                background=purple(0.18),
                border=f"1px solid {purple(0.35)}",
                border_radius="9999px",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.fragment(),
        ),
        rx.vstack(
            rx.text(
                label,
                size="3",
                weight="bold",
                color=rx.cond(is_active, TEXT_PRIMARY, white(0.3)),
                transition="color 0.15s ease",
            ),
            rx.text(
                description,
                size="2",
                color=rx.cond(is_active, TEXT_SECONDARY, white(0.25)),
                line_height="1.55",
                transition="color 0.15s ease",
            ),
            spacing="2",
            align="start",
            padding_right="1.75rem",  # avoid overlap with tick
        ),
        position="relative",
        on_click=AccountState.set_experience_level(label),
        flex="1",
        padding="1rem 1rem 1.125rem 1rem",
        border_radius="0.75rem",
        background=rx.cond(is_active, white(0.055), white(0.02)),
        border=rx.cond(
            is_active, f"1px solid {white(0.13)}", f"1px solid {white(0.05)}"
        ),
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={
            "background": rx.cond(is_active, white(0.055), white(0.033)),
            "border_color": rx.cond(is_active, white(0.13), white(0.085)),
        },
        min_height="5.5rem",
    )


# ── Period toggle ─────────────────────────────────────────────────────────────


def _period_btn(period: str) -> rx.Component:
    is_active = AccountState.default_chart_period == period
    return rx.box(
        rx.text(
            period,
            size="1",
            font_weight=rx.cond(is_active, "600", "400"),
            color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED),
        ),
        on_click=AccountState.set_default_chart_period(period),
        height="1.625rem",
        padding="0 0.5625rem",
        border_radius="0.3125rem",
        background=rx.cond(is_active, white(0.09), "transparent"),
        border=rx.cond(is_active, f"1px solid {white(0.14)}", "1px solid transparent"),
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={"background": rx.cond(is_active, white(0.09), white(0.04))},
        display="inline-flex",
        align_items="center",
        justify_content="center",
    )


# ── Preferences panel ─────────────────────────────────────────────────────────


def preferences_panel() -> rx.Component:
    return _card(
        _card_header(
            "sliders-horizontal",
            "Preferences",
            "Customise how the app looks and behaves for you.",
        ),
        _divider(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.text(
                        "Experience level",
                        size="2",
                        weight="medium",
                        color=TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Affects UI complexity, tooltips, and suggested frameworks.",
                        size="2",
                        color=TEXT_MUTED,
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.hstack(
                    _exp_card(
                        "Beginner",
                        "Simplified views, guided frameworks, helpful tooltips throughout.",
                    ),
                    _exp_card(
                        "Experienced",
                        "Full data density, advanced metrics, raw mode unlocked.",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            padding="1.25rem 1.5rem",
        ),
        _divider(),
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Default chart period",
                        size="2",
                        weight="medium",
                        color=TEXT_PRIMARY,
                    ),
                    rx.text(
                        "The timeframe shown when you first open any ticker.",
                        size="2",
                        color=TEXT_MUTED,
                    ),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                rx.hstack(
                    *[_period_btn(p) for p in DEFAULT_PERIOD_OPTIONS],
                    spacing="0",
                    gap="0.125rem",
                    padding="0.1875rem",
                    background=white(0.03),
                    border=f"1px solid {white(0.07)}",
                    border_radius="0.4375rem",
                    flex_shrink="0",
                ),
                align="center",
                spacing="4",
                width="100%",
            ),
            padding="1.25rem 1.5rem",
        ),
        _divider(),
        rx.hstack(
            rx.cond(
                AccountState.save_msg != "",
                _feedback(AccountState.save_msg),
                rx.cond(
                    AccountState.save_error != "",
                    _feedback(AccountState.save_error, is_error=True),
                    rx.cond(
                        AccountState.prefs_dirty,
                        rx.text("Unsaved changes", size="2", color=TEXT_MUTED),
                        rx.fragment(),
                    ),
                ),
            ),
            rx.spacer(),
            _loading_btn(
                "Save changes",
                on_click=AccountState.save_all,
                loading_var=AccountState.loading_save,
            ),
            align="center",
            width="100%",
            padding="0.875rem 1.5rem",
        ),
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
                label,
                size="2",
                color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED),
                font_weight=rx.cond(is_active, "500", "400"),
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
        _nav_item("preferences", "sliders-horizontal", "Preferences"),
        spacing="1",
        width="10.5rem",
        flex_shrink="0",
        align="start",
    )


# ── Main layout ───────────────────────────────────────────────────────────────


def account_layout() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.cond(
                AccountState.active_tab == "profile",
                rx.vstack(profile_panel(), delete_card(), spacing="3", width="100%"),
                rx.fragment(),
            ),
            rx.cond(
                AccountState.active_tab == "preferences",
                preferences_panel(),
                rx.fragment(),
            ),
            flex="1",
            min_width="0",
        ),
        spacing="8",
        align="start",
        width="100%",
    )
