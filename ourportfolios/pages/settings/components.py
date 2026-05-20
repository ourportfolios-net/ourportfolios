"""Settings page UI components."""

from collections.abc import Callable
from typing import Any

import reflex as rx

from ourportfolios.components.category_toggle_card import category_toggle_card
from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.settings.state import DEFAULT_PERIOD_OPTIONS, SettingsState
from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.primitives import (
    body_text,
    divider,
    heading,
    icon_container,
    label_text,
    muted_text,
    spacer,
    subheading,
    surface_box,
)
from ourportfolios.ui.theme import (
    BUTTON_GHOST_SM,
    CARD_BORDER,
    ERROR_COLOR,
    INPUT_STYLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    red,
    white,
)
from ourportfolios.ui.theme.surfaces import (
    RADIUS_4XS,
    RADIUS_BUTTON,
    RADIUS_PILL,
    RADIUS_SURFACE,
)
from ourportfolios.ui.tokens import RADIUS_2XS

# Type Aliases for cleaner code
StyleDict = dict[str, Any]
EventHandler = rx.event.EventSpec | list[rx.event.EventSpec] | Callable | Any
# ── Primitives ────────────────────────────────────────────────────────────────


def _input_compact_style() -> StyleDict:
    return {
        **INPUT_STYLE,
        "height": "2.125rem",
        "font_size": "0.875rem",
        "width": "100%",
    }


def _input_dialog_style() -> StyleDict:
    return {
        **INPUT_STYLE,
        "height": "2.625rem",
        "font_size": "0.9375rem",
        "width": "100%",
    }


def _ghost_button_style() -> StyleDict:
    return {
        **BUTTON_GHOST_SM,
        "height": "2.125rem",
        "padding": "0 0.875rem",
        "display": "inline-flex",
        "align_items": "center",
        "justify_content": "center",
        "flex_shrink": "0",
        "font_size": "0.8125rem",
        "font_weight": "500",
    }


def _ghost_button(label: str, on_click: EventHandler) -> rx.Component:
    return rx.box(
        rx.text(label, size="2", font_weight="500"),
        on_click=on_click,
        **_ghost_button_style(),
    )


def _loading_button(
    label: str,
    on_click: EventHandler,
    *,
    loading_var: bool | rx.Var[bool],
) -> rx.Component:
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
        **_ghost_button_style(),
    )


def _feedback(msg: str | rx.Var[str], *, is_error: bool = False) -> rx.Component:
    color = ERROR_COLOR if is_error else "rgba(52,211,153,0.9)"
    return rx.hstack(
        rx.icon("circle-alert" if is_error else "check-check", size=12, color=color),
        rx.text(msg, size="2", color=color),
        spacing="2",
        align="center",
    )


def _password_action_button() -> rx.Component:
    return rx.text(
        "Change password",
        size="1",
        color=white(0.5),
        text_decoration="none",
        cursor="pointer",
        transition="color 0.15s ease, text-decoration 0.15s ease",
        _hover={"color": "white", "text_decoration": "underline"},
        on_click=SettingsState.open_password_dialog,
        display="inline",
    )


def _edit_link(label: str, on_click: EventHandler) -> rx.Component:
    return rx.text(
        label,
        size="1",
        color=white(0.5),
        text_decoration="none",
        cursor="pointer",
        transition="color 0.15s ease, text-decoration 0.15s ease",
        _hover={"color": "white", "text_decoration": "underline"},
        on_click=on_click,
        display="inline",
    )


def _dlg_header(
    title: str,
    subtitle: str,
    on_close: EventHandler,
) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            heading(title, level=3, letter_spacing="-0.02em"),
            rx.cond(
                subtitle != "",
                muted_text(subtitle),
                rx.fragment(),
            ),
            spacing="0",
            align="start",
        ),
        spacer(),
        rx.dialog.close(
            rx.box(
                rx.icon("x", size=15, color=white(0.35)),
                on_click=on_close,
                padding="0.3rem",
                border_radius=RADIUS_PILL,
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


def _card(*children: rx.Component, border: str = CARD_BORDER) -> rx.Component:
    return surface_box(*children, padding="0", border=border, overflow="hidden")


def _card_header(
    icon_name: str,
    title: str,
    subtitle: str,
    color: str = "purple",
) -> rx.Component:
    return rx.hstack(
        icon_container(icon_name, color=color),
        rx.vstack(
            subheading(title, color=TEXT_PRIMARY, letter_spacing="-0.01em"),
            muted_text(subtitle),
            spacing="0",
        ),
        spacing="3",
        align="center",
        padding=rx.breakpoints(initial="0.875rem 1rem", md="1.25rem 1.5rem"),
        width="100%",
    )


# ── Password dialog ───────────────────────────────────────────────────────────


def _password_dialog() -> rx.Component:
    password_input_attrs = {
        "autocomplete": "new-password",
        "name": "op_security_pwd_field",
        "autocapitalize": "none",
        "autocorrect": "off",
        "spellcheck": "false",
        "data-1p-ignore": "true",
        "data-lpignore": "true",
    }

    content = rx.vstack(
        rx.vstack(
            body_text("Current password", font_weight="500"),
            rx.input(
                placeholder="Current password",
                value=SettingsState.old_password,
                on_change=SettingsState.set_old_password,
                type="password",
                custom_attrs={
                    **password_input_attrs,
                    "name": "op_current_password",
                },
                **_input_dialog_style(),
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
        rx.vstack(
            rx.vstack(
                body_text("New password", font_weight="500"),
                rx.input(
                    placeholder="At least 8 characters",
                    value=SettingsState.new_password,
                    on_change=SettingsState.set_new_password,
                    type="password",
                    custom_attrs={
                        **password_input_attrs,
                        "name": "op_new_password",
                    },
                    **_input_dialog_style(),
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            rx.vstack(
                body_text("Confirm new password", font_weight="500"),
                rx.input(
                    placeholder="Repeat your new password",
                    value=SettingsState.confirm_password,
                    on_change=SettingsState.set_confirm_password,
                    type="password",
                    custom_attrs={
                        **password_input_attrs,
                        "name": "op_confirm_password",
                    },
                    **_input_dialog_style(),
                ),
                spacing="2",
                width="100%",
                align="start",
            ),
            spacing="4",
            width="100%",
        ),
        rx.cond(
            SettingsState.password_error != "",
            _feedback(SettingsState.password_error, is_error=True),
            rx.fragment(),
        ),
        rx.hstack(
            _ghost_button("Cancel", on_click=SettingsState.close_password_dialog),
            _loading_button(
                "Update password",
                on_click=SettingsState.save_password,
                loading_var=SettingsState.loading_password,
            ),
            spacing="2",
            justify="end",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=SettingsState.password_dialog_open,
            on_close=SettingsState.close_password_dialog,
            on_open_change=SettingsState.set_password_dialog_open,
            title="Change password",
            title_size="5",
            width="90vw",
            max_width="30rem",
            height="fit-content",
            padding="1.75rem",
        ),
    )


# ── Delete dialog ─────────────────────────────────────────────────────────────


def _delete_dialog() -> rx.Component:
    content = rx.vstack(
        body_text(
            "This permanently removes all your data. There is no way to undo this.",
            color=white(0.62),
        ),
        rx.vstack(
            rx.flex(
                body_text("Type", color=white(0.58)),
                body_text(
                    SettingsState.delete_confirmation_token,
                    font_weight="700",
                    font_family="monospace",
                    color=red(0.82),
                    letter_spacing="0.02em",
                ),
                body_text("to confirm.", color=white(0.58)),
                gap="0.35rem",
                align="center",
                width="100%",
                wrap="wrap",
            ),
            rx.input(
                placeholder=SettingsState.delete_confirmation_token,
                value=SettingsState.delete_confirm_text,
                on_change=SettingsState.set_delete_confirm_text,
                style=_input_dialog_style(),
                _placeholder={"color": white(0.35)},
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
        rx.cond(
            SettingsState.delete_error != "",
            _feedback(SettingsState.delete_error, is_error=True),
            rx.fragment(),
        ),
        divider(),
        rx.hstack(
            _ghost_button("Cancel", on_click=SettingsState.close_delete_dialog),
            rx.box(
                rx.cond(
                    SettingsState.loading_delete,
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Deleting…", size="2", color=red(0.6)),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Delete account",
                        size="2",
                        font_weight="500",
                        color=red(0.8),
                    ),
                ),
                on_click=SettingsState.confirm_delete_account,
                height="2.125rem",
                padding="0 0.875rem",
                background=red(0.07),
                border=f"1px solid {red(0.18)}",
                border_radius=RADIUS_2XS,
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
        spacing="5",
        width="100%",
    )

    return common_dialog(
        content,
        CommonDialogConfig(
            is_open=SettingsState.delete_dialog_open,
            on_close=SettingsState.close_delete_dialog,
            on_open_change=SettingsState.set_delete_dialog_open,
            title="Delete account",
            title_size="5",
            width="90vw",
            max_width="32rem",
            height="fit-content",
            padding="2rem",
        ),
    )


def profile_panel() -> rx.Component:
    return _card(
        _card_header("user", "Profile", "Manage your identity and sign-in settings."),
        rx.box(
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.flex(
                            rx.hstack(
                                rx.vstack(
                                    label_text("Display name"),
                                    rx.cond(
                                        SettingsState.display_name_editing,
                                        rx.input(
                                            value=SettingsState.display_name_draft,
                                            on_change=SettingsState.set_display_name_draft,
                                            **_input_compact_style(),
                                            max_width="20rem",
                                        ),
                                        body_text(
                                            SettingsState.display_name,
                                            font_weight="500",
                                            color=TEXT_PRIMARY,
                                        ),
                                    ),
                                    spacing="1",
                                    align="start",
                                    min_width="0",
                                    flex="1",
                                ),
                                min_width="0",
                                align="start",
                                flex="1",
                            ),
                            rx.cond(
                                SettingsState.display_name_editing,
                                rx.hstack(
                                    _edit_link(
                                        "Cancel",
                                        SettingsState.cancel_display_name_edit,
                                    ),
                                    _loading_button(
                                        "Save",
                                        on_click=SettingsState.save_display_name,
                                        loading_var=SettingsState.loading_save,
                                    ),
                                    spacing="3",
                                    align="center",
                                    flex_shrink="0",
                                ),
                                _edit_link(
                                    "Edit",
                                    SettingsState.start_display_name_edit,
                                ),
                            ),
                            align="center",
                            width="100%",
                            gap="1rem",
                            justify="between",
                        ),
                        rx.flex(
                            rx.hstack(
                                rx.icon("mail", size=13, color=white(0.28)),
                                label_text("Email"),
                                body_text(AuthState.user_email, color=TEXT_PRIMARY),
                                spacing="2",
                                align="center",
                                min_width="0",
                                flex="1",
                            ),
                            rx.text(
                                "Edit",
                                size="1",
                                color=TEXT_MUTED,
                                _hover={"cursor": "not-allowed"},
                                flex_shrink="0",
                            ),
                            align="center",
                            width="100%",
                            gap="1rem",
                            justify="between",
                            wrap="wrap",
                        ),
                        rx.flex(
                            rx.hstack(
                                rx.icon("lock-keyhole", size=13, color=white(0.28)),
                                label_text("Password"),
                                body_text("••••••••", color=TEXT_PRIMARY),
                                spacing="2",
                                align="center",
                            ),
                            _password_action_button(),
                            align="center",
                            width="100%",
                            gap="1rem",
                            justify="between",
                        ),
                        spacing="3",
                        width="100%",
                        align="start",
                    ),
                    width="100%",
                    background=white(0.015),
                    border=f"1px solid {white(0.06)}",
                    border_radius=RADIUS_SURFACE,
                    padding=rx.breakpoints(initial="0.75rem", md="1rem"),
                ),
                spacing="3",
                width="100%",
            ),
            padding=rx.breakpoints(initial="0.875rem 1rem", md="1.25rem 1.5rem"),
        ),
        rx.box(
            rx.cond(
                SettingsState.save_msg != "",
                _feedback(SettingsState.save_msg),
                rx.cond(
                    SettingsState.save_error != "",
                    _feedback(SettingsState.save_error, is_error=True),
                    rx.fragment(),
                ),
            ),
            padding=rx.breakpoints(
                initial="0 1rem 0.875rem 1rem",
                md="0 1.5rem 1.125rem 1.5rem",
            ),
            width="100%",
        ),
        _password_dialog(),
    )


# ── Delete card ───────────────────────────────────────────────────────────────


def delete_card() -> rx.Component:
    return _card(
        rx.flex(
            rx.vstack(
                subheading("Delete account", color=TEXT_PRIMARY),
                muted_text("Permanently removes your account and all associated data."),
                spacing="1",
                align="start",
                flex="1",
            ),
            rx.box(
                rx.text("Delete account", size="2", font_weight="500", color=red(0.75)),
                on_click=SettingsState.open_delete_dialog,
                height="2.125rem",
                padding="0 0.875rem",
                background=red(0.05),
                border=f"1px solid {red(0.14)}",
                border_radius=RADIUS_2XS,
                cursor="pointer",
                transition="all 0.15s ease",
                _hover={"background": red(0.1), "border_color": red(0.26)},
                display="inline-flex",
                align_items="center",
                flex_shrink="0",
            ),
            align="center",
            width="100%",
            padding=rx.breakpoints(initial="0.875rem 1rem", md="1.125rem 1.5rem"),
            gap="0.75rem",
            justify="between",
            wrap="wrap",
        ),
        _delete_dialog(),
        border=f"1px solid {red(0.1)}",
    )


# ── Experience cards ──────────────────────────────────────────────────────────


def _exp_card(label: str, description: str) -> rx.Component:
    is_active = SettingsState.experience_level == label
    return category_toggle_card(
        title=label,
        checked=is_active,
        on_change=lambda _: SettingsState.set_experience_level(label),
        on_click=SettingsState.set_experience_level(label),
        body=rx.text(
            description,
            size="2",
            color=rx.cond(is_active, white(0.68), white(0.35)),
            line_height="1.55",
            transition="color 0.15s ease",
        ),
    )


# ── Period toggle ─────────────────────────────────────────────────────────────


def _period_button(period: str) -> rx.Component:
    is_active = SettingsState.default_chart_period == period
    return rx.box(
        rx.text(
            period,
            size="1",
            font_weight=rx.cond(is_active, "600", "400"),
            color=rx.cond(is_active, TEXT_PRIMARY, TEXT_MUTED),
        ),
        on_click=SettingsState.set_default_chart_period(period),
        height="1.625rem",
        padding="0 0.5625rem",
        border_radius=RADIUS_4XS,
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
        rx.box(
            rx.vstack(
                rx.vstack(
                    subheading("Experience level", color=TEXT_PRIMARY),
                    muted_text(
                        "Affects UI complexity, tooltips, and suggested frameworks.",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.grid(
                    _exp_card(
                        "Beginner",
                        "Simplified views, guided frameworks, helpful tooltips throughout.",
                    ),
                    _exp_card(
                        "Experienced",
                        "Full data density, advanced metrics, raw mode unlocked.",
                    ),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            padding=rx.breakpoints(initial="0.875rem 1rem", md="1.25rem 1.5rem"),
            width="100%",
        ),
        rx.box(
            rx.flex(
                rx.vstack(
                    subheading("Default chart period", color=TEXT_PRIMARY),
                    muted_text("The timeframe shown when you first open any ticker."),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                rx.hstack(
                    *[_period_button(p) for p in DEFAULT_PERIOD_OPTIONS],
                    spacing="0",
                    gap="0.125rem",
                    padding="0.1875rem",
                    background=white(0.03),
                    border=f"1px solid {white(0.07)}",
                    border_radius=RADIUS_2XS,
                    flex_shrink="0",
                ),
                align="center",
                gap="1rem",
                width="100%",
                wrap="wrap",
                justify="between",
            ),
            padding=rx.breakpoints(initial="0.875rem 1rem", md="1.25rem 1.5rem"),
            width="100%",
        ),
        rx.flex(
            rx.cond(
                SettingsState.save_msg != "",
                _feedback(SettingsState.save_msg),
                rx.cond(
                    SettingsState.save_error != "",
                    _feedback(SettingsState.save_error, is_error=True),
                    rx.cond(
                        SettingsState.prefs_dirty,
                        muted_text("Unsaved changes"),
                        rx.fragment(),
                    ),
                ),
            ),
            spacer(),
            _loading_button(
                "Save changes",
                on_click=SettingsState.save_all,
                loading_var=SettingsState.loading_save,
            ),
            align="center",
            width="100%",
            padding=rx.breakpoints(initial="0.875rem 1rem", md="1.125rem 1.5rem"),
            gap="0.75rem",
        ),
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────


def _nav_item(tab: str, icon_name: str, label: str) -> rx.Component:
    is_active = SettingsState.active_tab == tab
    return rx.box(
        rx.hstack(
            rx.icon(
                icon_name,
                size=14,
                color=rx.cond(is_active, white(0.75), white(0.28)),
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
        on_click=SettingsState.set_active_tab(tab),
        padding=rx.breakpoints(initial="0.4rem 0.625rem", md="0.5rem 0.75rem"),
        border_radius=RADIUS_BUTTON,
        background=rx.cond(is_active, white(0.05), "transparent"),
        border=rx.cond(is_active, f"1px solid {white(0.09)}", "1px solid transparent"),
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={"background": white(0.04)},
        width=rx.breakpoints(initial="auto", md="100%"),
        flex_shrink="0",
    )


def sidebar() -> rx.Component:
    return rx.flex(
        _nav_item("profile", "user", "Profile"),
        _nav_item("preferences", "sliders-horizontal", "Preferences"),
        direction=rx.breakpoints(initial="row", md="column"),
        gap="0.375rem",
        width=rx.breakpoints(initial="100%", md="10.5rem"),
        flex_shrink="0",
        align="start",
    )


# ── Main layout ───────────────────────────────────────────────────────────────


def settings_layout() -> rx.Component:
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(
                SettingsState.active_tab == "profile",
                rx.vstack(profile_panel(), delete_card(), spacing="3", width="100%"),
                rx.fragment(),
            ),
            rx.cond(
                SettingsState.active_tab == "preferences",
                preferences_panel(),
                rx.fragment(),
            ),
            flex="1",
            min_width="0",
        ),
        direction=rx.breakpoints(initial="column", md="row"),
        gap=rx.breakpoints(initial="1rem", md="2rem"),
        align="start",
        width="100%",
    )
