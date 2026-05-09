"""Contact form state management."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import reflex as rx

from ourportfolios.utils.email_client import load_email_config, send_contact_emails


class ContactState(rx.State):
    first_name: rx.Field[str] = rx.field(default="")
    last_name: rx.Field[str] = rx.field(default="")
    email: rx.Field[str] = rx.field(default="")
    subject: rx.Field[str] = rx.field(default="")
    message: rx.Field[str] = rx.field(default="")
    is_submitting: rx.Field[bool] = rx.field(default=False)
    submitted: rx.Field[bool] = rx.field(default=False)
    error: rx.Field[str] = rx.field(default="")

    # Rate limiting: timestamp log per email (sliding 24h window)
    _submission_log: rx.Field[dict[str, list[str]]] = rx.field(default={})
    _MAX_DAILY: int = 10
    _COOLDOWN_HOURS: int = 24

    @rx.var
    def form_is_valid(self) -> bool:
        return bool(
            self.first_name.strip()
            and self.last_name.strip()
            and self.email.strip()
            and "@" in self.email
            and "." in self.email
            and self.message.strip(),
        )

    @rx.event
    def set_first_name(self, value: str) -> None:
        self.first_name = value

    @rx.event
    def set_last_name(self, value: str) -> None:
        self.last_name = value

    @rx.event
    def set_email(self, value: str) -> None:
        self.email = value

    @rx.event
    def set_subject(self, value: str) -> None:
        self.subject = value

    @rx.event
    def set_message(self, value: str) -> None:
        self.message = value

    def _check_rate_limit(self, email: str) -> tuple[bool, str]:
        now = datetime.now(tz=UTC)
        cutoff = now - timedelta(hours=self._COOLDOWN_HOURS)

        if email not in self._submission_log:
            self._submission_log[email] = []

        self._submission_log[email] = [
            ts for ts in self._submission_log[email]
            if datetime.fromisoformat(ts) > cutoff
        ]

        if len(self._submission_log[email]) >= self._MAX_DAILY:
            return False, (
                f"Daily limit reached. "
                f"Maximum {self._MAX_DAILY} emails "
                f"per {self._COOLDOWN_HOURS} hours."
            )

        return True, ""

    def _record_submission(self, email: str) -> None:
        if email not in self._submission_log:
            self._submission_log[email] = []
        self._submission_log[email].append(
            datetime.now(tz=UTC).isoformat(),
        )

    @rx.event
    async def submit(self) -> AsyncGenerator[None]:
        if not self.form_is_valid:
            self.error = "Please fill in all required fields with a valid email."
            return
        self.error = ""
        self.is_submitting = True
        yield

        config = load_email_config()

        allowed, rate_error = self._check_rate_limit(self.email)
        if not allowed:
            self.error = rate_error
            self.is_submitting = False
            return
        yield

        success, error_msg = await send_contact_emails(
            self.first_name,
            self.last_name,
            self.email,
            self.subject,
            self.message,
            config=config,
        )

        if success:
            self._record_submission(self.email)
            self.is_submitting = False
            self.submitted = True
            self.first_name = ""
            self.last_name = ""
            self.email = ""
            self.subject = ""
            self.message = ""
        else:
            self.error = error_msg
            self.is_submitting = False

    @rx.event
    def reset_form(self) -> None:
        self.submitted = False
        self.error = ""
