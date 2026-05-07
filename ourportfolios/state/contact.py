import asyncio
from collections.abc import AsyncGenerator

import reflex as rx


class ContactState(rx.State):
    first_name: rx.Field[str] = rx.field(default="")
    last_name: rx.Field[str] = rx.field(default="")
    email: rx.Field[str] = rx.field(default="")
    subject: rx.Field[str] = rx.field(default="")
    message: rx.Field[str] = rx.field(default="")
    is_submitting: rx.Field[bool] = rx.field(default=False)
    submitted: rx.Field[bool] = rx.field(default=False)
    error: rx.Field[str] = rx.field(default="")

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

    def set_first_name(self, value: str) -> None:
        self.first_name = value

    def set_last_name(self, value: str) -> None:
        self.last_name = value

    def set_email(self, value: str) -> None:
        self.email = value

    def set_subject(self, value: str) -> None:
        self.subject = value

    def set_message(self, value: str) -> None:
        self.message = value

    async def submit(self) -> AsyncGenerator[None]:
        if not self.form_is_valid:
            self.error = "Please fill in all required fields with a valid email."
            return
        self.error = ""
        self.is_submitting = True
        yield

        await asyncio.sleep(1)
        self.is_submitting = False
        self.submitted = True
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.subject = ""
        self.message = ""

    def reset_form(self) -> None:
        self.submitted = False
        self.error = ""
