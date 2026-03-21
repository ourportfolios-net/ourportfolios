"""
Place at: ourportfolios/state/auth_state.py
"""

import secrets
import hashlib
import base64
import httpx
import reflex as rx

from ..auth_config import (
    AUTH_AVAILABLE,
    get_supabase,
    oauth_redirect_url,
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
)

_BLOCKED_DESTINATIONS = frozenset({"/auth", "/auth/callback", "/loading"})

_AUTH_ONLY_PREFIXES = (
    "/framework",
    "/portfolio",
    "/settings",
)


def _safe_destination(route: str) -> str:
    if not route:
        return "/home"
    path = route.split("?")[0].split("#")[0]
    if path in _BLOCKED_DESTINATIONS or not path.startswith("/"):
        return "/home"
    return path


def _is_auth_only(path: str) -> bool:
    for prefix in _AUTH_ONLY_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


def _generate_pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


_TOAST = dict(position="bottom-right", duration=4000)


class AuthState(rx.State):
    # ── Persisted cookies ─────────────────────────────────────────────────────
    auth_token: str = rx.Cookie(
        name="auth_token",
        secure=True,
        same_site="lax",
        max_age=3600,
        path="/",
    )
    auth_refresh_token: str = rx.Cookie(
        name="auth_refresh_token",
        secure=True,
        same_site="lax",
        max_age=604800,
        path="/",
    )
    intended_route: str = rx.Cookie(
        name="intended_route",
        secure=False,
        same_site="lax",
        max_age=300,
        path="/",
    )
    # PKCE verifier stored in a short-lived cookie so it survives redirects
    # across server restarts and multiple workers
    _pkce_verifier: str = rx.Cookie(
        name="pkce_verifier",
        secure=True,
        same_site="lax",
        max_age=300,
        path="/",
    )

    # ── Session ───────────────────────────────────────────────────────────────
    user_id: str = ""
    user_email: str = ""
    user_display_name: str = ""
    is_authenticated: bool = False
    is_guest: bool = False
    session_checked: bool = False
    auth_mode: str = "login"

    # ── Page-level gate ───────────────────────────────────────────────────────
    auth_checked: bool = False

    # ── Form ──────────────────────────────────────────────────────────────────
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    full_name: str = ""
    error: str = ""
    loading: bool = False

    # ── Resend confirmation ───────────────────────────────────────────────────
    show_resend: bool = False
    resend_loading: bool = False
    resend_sent: bool = False

    # ── Forgot password ───────────────────────────────────────────────────────
    forgot_open: bool = False
    forgot_email: str = ""
    forgot_error: str = ""
    forgot_loading: bool = False
    forgot_sent: bool = False

    # ── Reset password (after clicking email link) ────────────────────────────
    reset_new_password: str = ""
    reset_confirm_password: str = ""
    reset_error: str = ""
    reset_loading: bool = False
    reset_done: bool = False

    # ─────────────────────────────────────────────────────────────────────────
    # Computed
    # ─────────────────────────────────────────────────────────────────────────

    @rx.var
    def user_initial(self) -> str:
        src = self.user_display_name or self.user_email
        return src[0].upper() if src else "?"

    # ─────────────────────────────────────────────────────────────────────────
    # Setters
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    def set_mode_login(self):
        self.auth_mode = "login"
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.full_name = ""
        self.error = ""

    @rx.event
    def set_mode_register(self):
        self.auth_mode = "register"
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.full_name = ""
        self.error = ""

    @rx.event
    def set_email(self, value: str):
        self.email = value
        self.error = ""

    @rx.event
    def set_password(self, value: str):
        self.password = value
        self.error = ""

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.error = ""

    @rx.event
    def set_full_name(self, value: str):
        self.full_name = value

    @rx.event
    def set_user_display_name(self, value: str):
        self.user_display_name = value

    # ── Reset password setters ────────────────────────────────────────────────

    @rx.event
    def set_reset_new_password(self, value: str):
        self.reset_new_password = value
        self.reset_error = ""

    @rx.event
    def set_reset_confirm_password(self, value: str):
        self.reset_confirm_password = value
        self.reset_error = ""

    # ── Enter-key submit helpers ──────────────────────────────────────────────

    @rx.event
    def handle_login_on_enter(self, key: str):
        if key == "Enter":
            return AuthState.handle_login()

    @rx.event
    def handle_register_on_enter(self, key: str):
        if key == "Enter":
            return AuthState.handle_register()

    # ── Forgot password setters ───────────────────────────────────────────────

    @rx.event
    def open_forgot(self):
        self.forgot_open = True
        self.forgot_email = ""
        self.forgot_error = ""
        self.forgot_sent = False

    @rx.event
    def close_forgot(self):
        self.forgot_open = False

    @rx.event
    def set_forgot_email(self, value: str):
        self.forgot_email = value
        self.forgot_error = ""

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _store_session(self, user, session=None) -> None:
        self.user_id = str(user.id)
        self.user_email = user.email or ""
        self.user_display_name = (
            (user.user_metadata or {}).get("full_name", "")
            or (user.user_metadata or {}).get("name", "")
            or ""
        )
        self.is_authenticated = True
        self.is_guest = False
        if session:
            self.auth_token = session.access_token
            self.auth_refresh_token = session.refresh_token or ""

    def _clear_session(self) -> None:
        self.auth_token = ""
        self.auth_refresh_token = ""
        self.user_id = ""
        self.user_email = ""
        self.user_display_name = ""
        self.is_authenticated = False
        self.is_guest = True
        self.error = ""

    def _clear_form(self) -> None:
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.full_name = ""
        self.error = ""

    def _consume_intended_route(self) -> str:
        destination = _safe_destination(self.intended_route)
        self.intended_route = ""
        return destination

    def _parse_url_param(self, key: str) -> str:
        try:
            params = self.router.page.params
            value = params.get(key, "")
            if isinstance(value, list):
                return value[0] if value else ""
            return value or ""
        except Exception:
            return ""

    # ─────────────────────────────────────────────────────────────────────────
    # Navbar locked-link helpers
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    def redirect_to_login_from_current_page(self):
        self.intended_route = self.router.url.path
        return rx.redirect("/auth")

    @rx.event
    def redirect_to_login_with_destination(self, destination: str):
        self.intended_route = _safe_destination(destination)
        return rx.redirect("/auth")

    # ─────────────────────────────────────────────────────────────────────────
    # Login-page session check
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def check_existing_session(self):
        self.session_checked = False
        self.auth_mode = "login"

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
                destination = self._consume_intended_route()
                return rx.redirect(destination)
        except Exception:
            self._clear_session()

        self.session_checked = True

    # ─────────────────────────────────────────────────────────────────────────
    # Protected-page guard
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    async def require_auth(self):
        self.auth_checked = False

        if not AUTH_AVAILABLE:
            self.auth_checked = True
            return

        if self.is_authenticated:
            self.auth_checked = True
            return

        token = self.auth_token
        if token:
            try:
                supabase = get_supabase()
                response = supabase.auth.get_user(token)
                if response and response.user:
                    self._store_session(response.user)
                    self.auth_checked = True
                    return
            except Exception:
                self._clear_session()
                self.intended_route = self.router.url.path
                return [
                    rx.redirect("/auth"),
                    rx.toast.warning(
                        "Your session expired. Please sign in again.", **_TOAST
                    ),
                ]

        self.intended_route = self.router.url.path
        return rx.redirect("/auth")

    @rx.event
    async def require_account(self):
        async for update in self.require_auth():
            yield update

    @rx.event
    async def require_auth_strict(self):
        async for update in self.require_auth():
            yield update

    # ─────────────────────────────────────────────────────────────────────────
    # Guest
    # ─────────────────────────────────────────────────────────────────────────

    @rx.event
    def continue_as_guest(self):
        self._clear_form()
        self.is_guest = True
        self.is_authenticated = False

        raw = _safe_destination(self.intended_route)
        self.intended_route = ""

        if _is_auth_only(raw):
            return [
                rx.redirect("/home"),
                rx.toast.warning("This feature requires an account.", **_TOAST),
            ]

        return rx.redirect(raw)

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
            destination = self._consume_intended_route()
            return [
                rx.redirect(destination),
                rx.toast.success("Welcome back!", **_TOAST),
            ]

        self.loading = True
        self.error = ""
        self.show_resend = False
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_in_with_password(
                {"email": self.email, "password": self.password}
            )
            if response.session:
                self._store_session(response.user, response.session)
                self._clear_form()
                name = self.user_display_name or response.user.email or "back"
                destination = self._consume_intended_route()
                return [
                    rx.redirect(destination),
                    rx.toast.success(f"Welcome back, {name}!", **_TOAST),
                ]
            else:
                self.error = "Invalid credentials."
                return rx.toast.error("Invalid email or password.", **_TOAST)
        except Exception as e:
            msg = str(e).lower()
            if "email not confirmed" in msg:
                self.show_resend = True
                self.error = "Please confirm your email before signing in."
            else:
                self.error = str(e)
                return rx.toast.error(f"Sign in failed: {e}", **_TOAST)
        finally:
            self.loading = False

    @rx.event
    async def handle_register(self):
        if not AUTH_AVAILABLE:
            self._clear_form()
            destination = self._consume_intended_route()
            return [
                rx.redirect(destination),
                rx.toast.success("Account created! Welcome.", **_TOAST),
            ]

        if self.password != self.confirm_password:
            self.error = "Passwords do not match."
            return rx.toast.error("Passwords do not match.", **_TOAST)

        self.loading = True
        self.error = ""
        try:
            supabase = get_supabase()
            response = supabase.auth.sign_up(
                {
                    "email": self.email,
                    "password": self.password,
                    "options": {"email_redirect_to": oauth_redirect_url()},
                }
            )
            if response.user:
                if response.session:
                    self._store_session(response.user, response.session)
                    self._clear_form()
                    destination = self._consume_intended_route()
                    return [
                        rx.redirect(destination),
                        rx.toast.success("Welcome! Your account is ready.", **_TOAST),
                    ]
                else:
                    self._clear_form()
                    return [
                        rx.redirect("/auth"),
                        rx.toast.info(
                            "Check your email to confirm your account.", **_TOAST
                        ),
                    ]
            else:
                self.error = "Registration failed."
                return rx.toast.error(
                    "Registration failed. Please try again.", **_TOAST
                )
        except Exception as e:
            self.error = str(e)
            return rx.toast.error(f"Registration failed: {e}", **_TOAST)
        finally:
            self.loading = False

    @rx.event
    async def resend_confirmation(self):
        if not self.email:
            self.error = "Enter your email above first."
            return
        self.resend_loading = True
        try:
            supabase = get_supabase()
            supabase.auth.resend({"type": "signup", "email": self.email})
            self.resend_sent = True
            self.show_resend = False
            return rx.toast.success(
                "Confirmation email resent. Check your inbox.", **_TOAST
            )
        except Exception as e:
            self.error = str(e)
            return rx.toast.error(f"Failed to resend: {e}", **_TOAST)
        finally:
            self.resend_loading = False

    @rx.event
    async def handle_google_login(self):
        if not AUTH_AVAILABLE:
            return
        try:
            verifier, challenge = _generate_pkce()
            self._pkce_verifier = verifier

            import urllib.parse

            params = urllib.parse.urlencode(
                {
                    "provider": "google",
                    "redirect_to": oauth_redirect_url(),
                    "code_challenge": challenge,
                    "code_challenge_method": "S256",
                }
            )
            url = f"{SUPABASE_URL}/auth/v1/authorize?{params}"
            return rx.redirect(url)
        except Exception as e:
            self.error = str(e)
            return rx.toast.error(f"Google sign in failed: {e}", **_TOAST)

    @rx.event
    async def handle_oauth_callback(self):
        if not AUTH_AVAILABLE:
            return rx.redirect("/home")

        token_hash = self._parse_url_param("token_hash")
        token_type = self._parse_url_param("type")
        if token_hash and token_type:
            try:
                supabase = get_supabase()
                response = supabase.auth.verify_otp(
                    {"token_hash": token_hash, "type": token_type}
                )
                if response.session:
                    self._store_session(response.user, response.session)
                    if token_type == "recovery":
                        return rx.redirect("/auth/reset-callback")
                    destination = self._consume_intended_route()
                    return [
                        rx.redirect(destination),
                        rx.toast.success(
                            f"Email confirmed! Welcome, {self.user_display_name or self.user_email}!",
                            **_TOAST,
                        ),
                    ]
            except Exception as e:
                self.error = str(e)
            return [
                rx.redirect("/auth"),
                rx.toast.error(
                    "Confirmation link expired. Please request a new one.", **_TOAST
                ),
            ]

        code = self._parse_url_param("code")
        if code:
            verifier = self._pkce_verifier
            self._pkce_verifier = ""
            if not verifier:
                return [
                    rx.redirect("/auth"),
                    rx.toast.warning("Sign in timed out. Please try again.", **_TOAST),
                ]
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{SUPABASE_URL}/auth/v1/token?grant_type=pkce",
                        json={"auth_code": code, "code_verifier": verifier},
                        headers={
                            "apikey": SUPABASE_ANON_KEY,
                            "Content-Type": "application/json",
                        },
                    )
                data = resp.json()
                if "error" in data:
                    raise Exception(data.get("error_description", data["error"]))

                access_token = data.get("access_token", "")
                refresh_token = data.get("refresh_token", "")
                if not access_token:
                    raise Exception("No access token returned.")

                supabase = get_supabase()
                user_response = supabase.auth.get_user(access_token)
                if not user_response or not user_response.user:
                    raise Exception("Could not retrieve user.")

                self.auth_token = access_token
                self.auth_refresh_token = refresh_token
                self._store_session(user_response.user)
                destination = self._consume_intended_route()
                return [
                    rx.redirect(destination),
                    rx.toast.success(
                        f"Welcome, {self.user_display_name or self.user_email}!",
                        **_TOAST,
                    ),
                ]
            except Exception as e:
                self.error = str(e)
                return [
                    rx.redirect("/auth"),
                    rx.toast.error(f"Sign in failed: {e}", **_TOAST),
                ]

        return [
            rx.redirect("/auth"),
            rx.toast.success("Email confirmed! Please sign in.", **_TOAST),
        ]

    @rx.event
    async def logout(self):
        if AUTH_AVAILABLE:
            try:
                supabase = get_supabase()
                supabase.auth.sign_out()
            except Exception:
                pass
        current_path = self.router.url.path
        self._clear_session()
        self._clear_form()
        if _is_auth_only(current_path):
            return [
                rx.redirect("/home"),
                rx.toast.info("Signed out. Browsing as guest.", **_TOAST),
            ]
        return rx.toast.info("Signed out. Browsing as guest.", **_TOAST)

    # ── Forgot password ───────────────────────────────────────────────────────

    @rx.event
    async def handle_forgot_password(self):
        if not self.forgot_email.strip():
            self.forgot_error = "Enter your email address."
            return

        self.forgot_loading = True
        self.forgot_error = ""
        try:
            if AUTH_AVAILABLE:
                supabase = get_supabase()
                supabase.auth.reset_password_email(self.forgot_email.strip())
            self.forgot_sent = True
        except Exception as e:
            self.forgot_error = str(e)
        finally:
            self.forgot_loading = False

    # ── Reset password ────────────────────────────────────────────────────────

    @rx.event
    async def handle_reset_callback(self):
        """Dedicated callback for password reset emails — no ambiguity with email confirmation."""
        if not AUTH_AVAILABLE:
            return rx.redirect("/auth/reset-password")

        token_hash = self._parse_url_param("token_hash")
        if not token_hash:
            return [
                rx.redirect("/auth"),
                rx.toast.error("Invalid or expired reset link.", **_TOAST),
            ]

        try:
            supabase = get_supabase()
            response = supabase.auth.verify_otp(
                {"token_hash": token_hash, "type": "recovery"}
            )
            if response.session:
                self._store_session(response.user, response.session)
                return rx.redirect("/auth/reset-password")
        except Exception as e:
            pass

        return [
            rx.redirect("/auth"),
            rx.toast.error("Reset link expired. Please request a new one.", **_TOAST),
        ]

    @rx.event
    async def handle_reset_password(self):
        if self.reset_new_password != self.reset_confirm_password:
            self.reset_error = "Passwords do not match."
            return

        if len(self.reset_new_password) < 8:
            self.reset_error = "Password must be at least 8 characters."
            return

        self.reset_loading = True
        self.reset_error = ""
        try:
            supabase = get_supabase()
            supabase.auth.update_user({"password": self.reset_new_password})
            self.reset_done = True
            self.reset_new_password = ""
            self.reset_confirm_password = ""
            return rx.toast.success("Password updated! Please sign in.", **_TOAST)
        except Exception as e:
            self.reset_error = str(e)
            return rx.toast.error(f"Failed to update password: {e}", **_TOAST)
        finally:
            self.reset_loading = False
