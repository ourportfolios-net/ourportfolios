"""Place at: ourportfolios/pages/settings/state.py"""

import reflex as rx
from ...auth_config import get_supabase, AUTH_AVAILABLE
from ...state.auth_state import AuthState

EXPERIENCE_OPTIONS = ["Beginner", "Experienced"]
DEFAULT_PERIOD_OPTIONS = ["1D", "1W", "1M", "3M", "1Y", "ALL"]

_TOAST = dict(position="bottom-right", duration=4000)


def _restore_session(auth) -> None:
    """Restore this user's session on the Supabase singleton before update_user."""
    supabase = get_supabase()
    supabase.auth.set_session(auth.auth_token, auth.auth_refresh_token)


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
    def set_active_tab(self, v: str):
        self.active_tab = v
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_display_name(self, v: str):
        self.display_name = v
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_display_name_draft(self, v: str):
        self.display_name_draft = v
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
    def set_experience_level(self, v: str):
        self.experience_level = v
        self.save_msg = ""
        self.save_error = ""

    @rx.event
    def set_default_chart_period(self, v: str):
        self.default_chart_period = v
        self.save_msg = ""
        self.save_error = ""

    # ── Password dialog setters ───────────────────────────────────────────────

    @rx.event
    def set_old_password(self, v: str):
        self.old_password = v
        self.password_error = ""

    @rx.event
    def set_new_password(self, v: str):
        self.new_password = v
        self.password_error = ""

    @rx.event
    def set_confirm_password(self, v: str):
        self.confirm_password = v
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
    def set_password_dialog_open(self, v: bool):
        self.password_dialog_open = v

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
    def set_delete_dialog_open(self, v: bool):
        self.delete_dialog_open = v

    @rx.event
    def set_delete_confirm_text(self, v: str):
        self.delete_confirm_text = v
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
            user = result.user
            if user is None:
                yield rx.redirect("/")
                return

            meta = user.user_metadata or {}
            name = meta.get("full_name") or auth.user_display_name or ""
            exp = meta.get("experience_level", "Beginner")
            period = meta.get("default_chart_period", "1M")

            self.display_name = name
            self.display_name_draft = name
            self.display_name_editing = False
            self._orig_name = name
            self.experience_level = exp
            self._orig_exp = exp
            self.default_chart_period = period
            self._orig_period = period

            auth.user_display_name = name

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
                _restore_session(auth)
                supabase = get_supabase()
                result = supabase.auth.update_user({"data": {"full_name": name}})
                if result.user is None:
                    raise Exception("Update failed — Supabase returned no user.")

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
                _restore_session(auth)
                supabase = get_supabase()
                result = supabase.auth.update_user(
                    {
                        "data": {
                            "experience_level": self.experience_level,
                            "default_chart_period": self.default_chart_period,
                        }
                    }
                )
                if result.user is None:
                    raise Exception("Update failed — Supabase returned no user.")

            self._orig_exp = self.experience_level
            self._orig_period = self.default_chart_period
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

                # Verify old password — sign_in_with_password also establishes
                # the session on the singleton so the subsequent update_user is
                # authenticated correctly without needing set_session.
                verify = supabase.auth.sign_in_with_password(
                    {"email": auth.user_email, "password": self.old_password}
                )
                if verify.user is None:
                    self.password_error = "Current password is incorrect."
                    return

                # Store the fresh tokens from re-auth
                if verify.session:
                    auth.auth_token = verify.session.access_token
                    auth.auth_refresh_token = (
                        verify.session.refresh_token or auth.auth_refresh_token
                    )

                result = supabase.auth.update_user({"password": self.new_password})
                if result.user is None:
                    raise Exception(
                        "Password update failed — Supabase returned no user."
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
                # Requires service role key on the client.
                # If using anon key only, replace with a Supabase Edge Function.
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
