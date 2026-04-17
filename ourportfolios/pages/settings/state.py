"""Settings page state for profile, preferences, password, and account deletion."""

import reflex as rx
from ...auth_config import AUTH_AVAILABLE, get_supabase, supabase_update_user
from ...state.auth_state import AuthState
from ...state.prefs_state import PrefsState

EXPERIENCE_OPTIONS = ["Beginner", "Experienced"]
DEFAULT_PERIOD_OPTIONS = ["1D", "1W", "1M"]

_TOAST = dict(position="bottom-right", duration=4000)


class SettingsState(rx.State):
    active_tab: str = "profile"

    # ── Profile ───────────────────────────────────────────────────────────────
    display_name: str = ""
    _orig_name: str = ""
    display_name_editing: bool = False
    display_name_draft: str = ""

    # ── Preferences ───────────────────────────────────────────────────────────
    experience_level: str = "Beginner"
    default_chart_period: str = "1M"
    _orig_exp: str = "Beginner"
    _orig_period: str = "1M"

    # ── Save feedback ─────────────────────────────────────────────────────────
    save_msg: str = ""
    save_error: str = ""
    loading_save: bool = False

    # ── Password dialog ───────────────────────────────────────────────────────
    password_dialog_open: bool = False
    old_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    password_error: str = ""
    password_msg: str = ""
    loading_password: bool = False

    # ── Delete dialog ─────────────────────────────────────────────────────────
    delete_dialog_open: bool = False
    delete_confirm_text: str = ""
    delete_error: str = ""
    loading_delete: bool = False

    # ─────────────────────────────────────────────────────────────────────────
    # Computed
    # ─────────────────────────────────────────────────────────────────────────

    @rx.var
    def profile_dirty(self) -> bool:
        return self.display_name != self._orig_name

    @rx.var
    def prefs_dirty(self) -> bool:
        return (
            self.experience_level != self._orig_exp
            or self.default_chart_period != self._orig_period
        )

    @rx.var
    def delete_confirmation_token(self) -> str:
        base = (self.display_name or "").strip().upper().replace(" ", "_")
        if not base:
            base = "ACCOUNT"
        return f"{base}_DELETE"

    # ── Setters ───────────────────────────────────────────────────────────────

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_display_name(self, value: str):
        self.display_name = value
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_display_name_draft(self, value: str):
        self.display_name_draft = value
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def start_display_name_edit(self):
        self.display_name_draft = self.display_name
        self.display_name_editing = True
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def cancel_display_name_edit(self):
        self.display_name_draft = self.display_name
        self.display_name_editing = False
        self.save_error = ""

    @rx.event
    def set_experience_level(self, value: str):
        self.experience_level = value
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_default_chart_period(self, value: str):
        self.default_chart_period = value
        self.save_msg = ""
        self.save_error = ""

    # ── Password dialog setters ───────────────────────────────────────────────

    @rx.event
    def set_old_password(self, value: str):
        self.old_password = value
        self.password_error = ""

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value
        self.password_error = ""

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.password_error = ""

    @rx.event
    def open_password_dialog(self):
        self.password_dialog_open = True
        self.old_password = ""
        self.new_password = ""
        self.confirm_password = ""
        self.password_error = ""
        self.password_msg = ""

    @rx.event
    def close_password_dialog(self):
        self.password_dialog_open = False

    @rx.event
    def set_password_dialog_open(self, is_open: bool):
        self.password_dialog_open = is_open

    # ── Delete dialog setters ─────────────────────────────────────────────────

    @rx.event
    def open_delete_dialog(self):
        self.delete_dialog_open = True
        self.delete_confirm_text = ""
        self.delete_error = ""

    @rx.event
    def close_delete_dialog(self):
        self.delete_dialog_open = False

    @rx.event
    def set_delete_dialog_open(self, is_open: bool):
        self.delete_dialog_open = is_open

    @rx.event
    def set_delete_confirm_text(self, value: str):
        self.delete_confirm_text = value
        self.delete_error = ""

    # ─────────────────────────────────────────────────────────────────────────
    # Load
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def load_settings(self):
        auth = await self.get_state(AuthState)
        if not auth.is_authenticated:
            yield rx.redirect("/")
            return

        if not AUTH_AVAILABLE:
            name = auth.user_display_name or ""
            self.display_name = name
            self.display_name_draft = name
            self._orig_name = name
            self.display_name_editing = False
            return

        try:
            supabase = get_supabase()
            result = supabase.auth.get_user(auth.auth_token)
            if result is None:
                yield rx.redirect("/")
                return
            user = result.user
            if user is None:
                yield rx.redirect("/")
                return

            metadata = user.user_metadata or {}
            display_name = metadata.get("full_name") or auth.user_display_name or ""

            # Clamp stored period to the 3 valid options
            stored_period = metadata.get("default_chart_period", "1M")
            chart_period = (
                stored_period if stored_period in DEFAULT_PERIOD_OPTIONS else "1M"
            )

            experience_level = metadata.get("experience_level", "Beginner")

            self.display_name = display_name
            self.display_name_draft = display_name
            self.display_name_editing = False
            self._orig_name = display_name
            self.experience_level = experience_level
            self._orig_exp = experience_level
            self.default_chart_period = chart_period
            self._orig_period = chart_period

            auth.user_display_name = display_name

            # Keep PrefsState in sync
            prefs = await self.get_state(PrefsState)
            prefs.experience_level = experience_level
            prefs.default_chart_period = chart_period

        except Exception as e:
            self.save_error = str(e)

    # ─────────────────────────────────────────────────────────────────────────
    # Save display name
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def save_display_name(self):
        self.loading_save = True
        self.save_msg = ""
        self.save_error = ""
        try:
            name = self.display_name_draft.strip()
            if not name:
                self.save_error = "Display name cannot be empty."
                return

            auth = await self.get_state(AuthState)

            if AUTH_AVAILABLE:
                await supabase_update_user(
                    auth.auth_token, {"data": {"full_name": name}}
                )

            auth.user_display_name = name
            self.display_name = name
            self.display_name_draft = name
            self._orig_name = name
            self.display_name_editing = False
            self.save_msg = "Saved"
            yield rx.toast.success("Display name updated.", **_TOAST)
        except Exception as e:
            self.save_error = str(e)
            yield rx.toast.error(f"Failed to save: {e}", **_TOAST)
        finally:
            self.loading_save = False

    # ─────────────────────────────────────────────────────────────────────────
    # Save preferences
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def save_all(self):
        self.loading_save = True
        self.save_msg = ""
        self.save_error = ""
        try:
            auth = await self.get_state(AuthState)

            if AUTH_AVAILABLE:
                await supabase_update_user(
                    auth.auth_token,
                    {
                        "data": {
                            "experience_level": self.experience_level,
                            "default_chart_period": self.default_chart_period,
                        }
                    },
                )

            self._orig_exp = self.experience_level
            self._orig_period = self.default_chart_period

            # Push to PrefsState immediately so other pages reflect it
            # without needing a reload
            prefs = await self.get_state(PrefsState)
            prefs.experience_level = self.experience_level
            prefs.default_chart_period = self.default_chart_period

            self.save_msg = "Saved"
            yield rx.toast.success("Preferences saved.", **_TOAST)
        except Exception as e:
            self.save_error = str(e)
            yield rx.toast.error(f"Failed to save: {e}", **_TOAST)
        finally:
            self.loading_save = False

    # ─────────────────────────────────────────────────────────────────────────
    # Password change
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def save_password(self):
        if not self.old_password:
            self.password_error = "Enter your current password."
            return
        if len(self.new_password) < 8:
            self.password_error = "New password must be at least 8 characters."
            return
        if self.new_password != self.confirm_password:
            self.password_error = "Passwords do not match."
            return

        self.loading_password = True
        self.password_error = ""
        try:
            auth = await self.get_state(AuthState)

            if AUTH_AVAILABLE:
                supabase = get_supabase()

                sign_in_response = supabase.auth.sign_in_with_password(
                    {"email": auth.user_email, "password": self.old_password}
                )
                if sign_in_response.user is None:
                    self.password_error = "Current password is incorrect."
                    return

                if sign_in_response.session:
                    auth.auth_token = sign_in_response.session.access_token
                    auth.auth_refresh_token = (
                        sign_in_response.session.refresh_token
                        or auth.auth_refresh_token
                    )

                await supabase_update_user(
                    auth.auth_token, {"password": self.new_password}
                )

            self.old_password = ""
            self.new_password = ""
            self.confirm_password = ""
            self.password_dialog_open = False
            self.password_msg = "Password updated."
            yield rx.toast.success("Password changed successfully.", **_TOAST)
        except Exception as e:
            msg = str(e)
            if any(k in msg.lower() for k in ("invalid", "credentials", "wrong")):
                self.password_error = "Current password is incorrect."
            else:
                self.password_error = msg
            yield rx.toast.error("Failed to change password.", **_TOAST)
        finally:
            self.loading_password = False

    # ─────────────────────────────────────────────────────────────────────────
    # Delete account
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def confirm_delete_account(self):
        entered = self.delete_confirm_text.strip().upper().replace(" ", "_")
        if entered != self.delete_confirmation_token:
            self.delete_error = f'Type "{self.delete_confirmation_token}" to confirm.'
            return

        self.loading_delete = True
        self.delete_error = ""
        try:
            auth = await self.get_state(AuthState)

            if AUTH_AVAILABLE:
                supabase = get_supabase()
                supabase.auth.admin.delete_user(auth.user_id)
                supabase.auth.sign_out()

            auth.auth_token = ""
            auth.auth_refresh_token = ""
            auth.user_id = ""
            auth.user_email = ""
            auth.user_display_name = ""
            auth.is_authenticated = False
            auth.is_guest = True

            self.delete_dialog_open = False
            yield rx.redirect("/")
            yield rx.toast.info("Your account has been deleted.", **_TOAST)
        except Exception as e:
            self.delete_error = str(e)
            yield rx.toast.error(f"Failed to delete account: {e}", **_TOAST)
        finally:
            self.loading_delete = False
