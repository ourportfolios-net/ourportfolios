"""
Place at: ourportfolios/state/auth_state.py
"""

import reflex as rx

from ..auth_config import AUTH_AVAILABLE, get_supabase, oauth_redirect_url


class AuthState(rx.State):
    # ── Persisted ─────────────────────────────────────────────────────────────
    auth_token: str = rx.Cookie(
        name="auth_token",
        secure=True,
        same_site="lax",
        max_age=3600,
        path="/",
    )

    # ── Session ───────────────────────────────────────────────────────────────
    user_id: str = ""
    user_email: str = ""
    user_display_name: str = ""  # editable display name, set from account page
    is_authenticated: bool = False
    is_guest: bool = False
    session_checked: bool = False  # flips True once check_existing_session finishes
    auth_mode: str = "login"  # "login" | "register"

    @rx.event
    def set_mode_login(self):
        self.auth_mode = "login"
        self.error = ""

    @rx.event
    def set_mode_register(self):
        self.auth_mode = "register"
        self.error = ""

    # ── Form ──────────────────────────────────────────────────────────────────
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    full_name: str = ""
    error: str = ""
    loading: bool = False

    # ─────────────────────────────────────────────────────────────────────────
    # Computed
    # ─────────────────────────────────────────────────────────────────────────

    @rx.var
    def user_initial(self) -> str:
        """First character of display name or email, uppercased."""
        src = self.user_display_name or self.user_email
        return src[0].upper() if src else "?"

    # ─────────────────────────────────────────────────────────────────────────
    # Setters
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    def set_email(self, value: str) -> None:
        self.email = value
        self.error = ""

    @rx.event
    def set_password(self, value: str) -> None:
        self.password = value
        self.error = ""

    @rx.event
    def set_confirm_password(self, value: str) -> None:
        self.confirm_password = value
        self.error = ""

    @rx.event
    def set_full_name(self, value: str) -> None:
        self.full_name = value

    @rx.event
    def set_user_display_name(self, value: str) -> None:
        self.user_display_name = value

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _store_session(self, user) -> None:
        self.user_id = str(user.id)
        self.user_email = user.email or ""
        self.user_display_name = (
            (user.user_metadata or {}).get("full_name", "")
            or (user.user_metadata or {}).get("name", "")
            or ""
        )
        self.is_authenticated = True
        self.is_guest = False

    def _clear_session(self) -> None:
        self.auth_token = ""
        self.user_id = ""
        self.user_email = ""
        self.user_display_name = ""
        self.is_authenticated = False
        self.is_guest = True  # ← becomes guest after logout, not unauthenticated
        self.error = ""

    def _clear_form(self) -> None:
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.full_name = ""
        self.error = ""

    # ─────────────────────────────────────────────────────────────────────────
    # Session check (used on /login on_load)
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def check_existing_session(self):
        """
        Fires on /login on_load.
        - Keeps session_checked=False (screen hidden) while checking.
        - If valid token found → redirect to /home (form never shown).
        - Otherwise → flip session_checked=True to reveal the form.
        """
        self.session_checked = False

        # Set form mode based on which route triggered the load
        self.auth_mode = "register" if "/register" in self.router.url.path else "login"

        if not AUTH_AVAILABLE:
            self.session_checked = True
            return

        token = self.auth_token
        if not token:
            self.session_checked = True
            return

        try:
            supabase = get_supabase()
            response = supabase.auth.get_user(token)
            if response and response.user:
                self._store_session(response.user)
                # Redirect fires — session_checked stays False — form never renders
                return rx.redirect("/home")
        except Exception:
            self._clear_session()

        self.session_checked = True

    # ─────────────────────────────────────────────────────────────────────────
    # Page guards
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def require_auth(self):
        """Allows authenticated users and guests. Blocks truly unauthenticated."""
        if not AUTH_AVAILABLE:
            return
        if self.is_authenticated or self.is_guest:
            return
        token = self.auth_token
        if not token:
            return rx.redirect("/login")
        try:
            supabase = get_supabase()
            response = supabase.auth.get_user(token)
            if response and response.user:
                self._store_session(response.user)
            else:
                self._clear_session()
                return rx.redirect("/login")
        except Exception:
            self._clear_session()
            return rx.redirect("/login")

    @rx.event
    async def require_auth_strict(self):
        """Blocks both unauthenticated users AND guests."""
        if not AUTH_AVAILABLE:
            return
        if self.is_authenticated:
            return
        # guests get bounced here
        self._clear_session()
        return rx.redirect("/login")

    # ─────────────────────────────────────────────────────────────────────────
    # Guest
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    def continue_as_guest(self):
        self._clear_form()
        self.is_guest = True
        self.is_authenticated = False
        return rx.redirect("/home")

    # ─────────────────────────────────────────────────────────────────────────
    # Auth actions
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def handle_login(self):
        if not AUTH_AVAILABLE:
            self._clear_form()
            self.is_authenticated = True
            self.is_guest = False
            self.user_email = "dev@local"
            self.user_id = "dev"
            return [
                rx.redirect("/home"),
                rx.toast.success(
                    "Welcome back!", position="bottom-right", duration=3000
                ),
            ]

        self.loading = True
        self.error = ""
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_in_with_password(
                {"email": self.email, "password": self.password}
            )
            if response.session:
                self.auth_token = response.session.access_token
                self._store_session(response.user)
                self._clear_form()
                name = self.user_display_name or response.user.email or "back"
                return [
                    rx.redirect("/home"),
                    rx.toast.success(
                        f"Welcome back, {name}!", position="bottom-right", duration=3000
                    ),
                ]
            else:
                self.error = "Invalid credentials."
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False

    @rx.event
    async def handle_register(self):
        if not AUTH_AVAILABLE:
            self._clear_form()
            return [
                rx.redirect("/home"),
                rx.toast.success(
                    "Account created! Welcome.", position="bottom-right", duration=3000
                ),
            ]

        if self.password != self.confirm_password:
            self.error = "Passwords do not match."
            return

        self.loading = True
        self.error = ""
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_up(
                {"email": self.email, "password": self.password}
            )
            if response.user:
                if response.session:
                    self.auth_token = response.session.access_token
                    self._store_session(response.user)
                    self._clear_form()
                    return [
                        rx.redirect("/home"),
                        rx.toast.success(
                            "Welcome! Your account is ready.",
                            position="bottom-right",
                            duration=3000,
                        ),
                    ]
                else:
                    self._clear_form()
                    return rx.redirect("/login?registered=1")
            else:
                self.error = "Registration failed."
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False

    @rx.event
    async def handle_google_login(self):
        if not AUTH_AVAILABLE:
            return
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_in_with_oauth(
                {"provider": "google", "options": {"redirect_to": oauth_redirect_url()}}
            )
            if response.url:
                return rx.redirect(response.url)
        except Exception as e:
            self.error = str(e)

    @rx.event
    async def handle_oauth_callback(self):
        pass

    @rx.event
    async def logout(self):
        """
        Signs out and demotes to guest — stays on current page.
        No redirect. Guest badge appears in navbar immediately.
        """
        if AUTH_AVAILABLE:
            try:
                supabase = get_supabase()
                supabase.auth.sign_out()
            except Exception:
                pass
        self._clear_session()  # _clear_session now sets is_guest=True
        self._clear_form()
        return rx.toast.info(
            "Signed out. Browsing as guest.", position="bottom-right", duration=3000
        )
