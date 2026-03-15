"""Place at: ourportfolios/pages/account/state.py"""

import reflex as rx
from ...state.auth_state import AuthState

EXPERIENCE_OPTIONS = ["Beginner", "Experienced"]


class AccountState(rx.State):
    active_tab: str = "profile"

    display_name: str = ""
    experience_level: str = "Beginner"

    _orig_name: str = ""
    _orig_exp: str = "Beginner"

    save_msg: str = ""
    save_error: str = ""
    loading_save: bool = False

    password_dialog_open: bool = False
    old_password: str = ""
    new_password: str = ""
    confirm_password: str = ""
    password_error: str = ""
    password_msg: str = ""
    loading_password: bool = False

    @rx.var
    def is_dirty(self) -> bool:
        return (
            self.display_name != self._orig_name
            or self.experience_level != self._orig_exp
        )

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
    def set_experience_level(self, v: str):
        self.experience_level = v
        self.save_msg = ""
        self.save_error = ""

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

    # ── Load ──────────────────────────────────────────────────────────────────

    @rx.event
    async def load_account(self):
        auth = await self.get_state(AuthState)
        if not auth.is_authenticated:
            yield rx.redirect("/")
            return
        name = auth.user_display_name or ""
        self.display_name = name
        self._orig_name = name

    # ── Save ──────────────────────────────────────────────────────────────────

    @rx.event
    async def save_all(self):
        self.loading_save = True
        self.save_msg = ""
        self.save_error = ""
        try:
            name = self.display_name.strip()

            # ── IMPORTANT ────────────────────────────────────────────────────
            # Wire your Supabase client here so the change persists across
            # page refreshes. Without this the in-memory update will be lost.
            #
            # from ...utils.supabase import supabase
            # result = supabase.auth.update_user({
            #     "data": {
            #         "full_name": name,
            #         "experience_level": self.experience_level,
            #     }
            # })
            # if result.user is None:
            #     raise Exception("Update failed.")
            # ─────────────────────────────────────────────────────────────────

            # Reflect immediately in AuthState (in-memory only until Supabase wired)
            auth = await self.get_state(AuthState)
            auth.user_display_name = name

            self.display_name = name
            self._orig_name = name
            self._orig_exp = self.experience_level
            self.save_msg = "Saved."
        except Exception as e:
            self.save_error = str(e)
        finally:
            self.loading_save = False

    # ── Password ──────────────────────────────────────────────────────────────

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
            # TODO: supabase.auth.update_user({"password": self.new_password})
            self.password_msg = "Password updated."
            self.old_password = ""
            self.new_password = ""
            self.confirm_password = ""
            self.password_dialog_open = False
        except Exception as e:
            self.password_error = str(e)
        finally:
            self.loading_password = False
