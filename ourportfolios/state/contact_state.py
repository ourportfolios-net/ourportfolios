"""Contact page state management."""

import reflex as rx

from ourportfolios.utils.database.database import get_company_session
from ourportfolios.utils.database.models import ContactSubmissionORM


class ContactState(rx.State):
    # Form fields
    name: str = ""
    email: str = ""
    subject: str = ""
    message: str = ""

    # Form state
    is_submitting: rx.Field[bool] = rx.field(default=False)
    is_submitted: rx.Field[bool] = rx.field(default=False)
    error: rx.Field[str] = rx.field(default="")

    # Setters
    def set_name(self, value: str) -> None:
        self.name = value

    def set_email(self, value: str) -> None:
        self.email = value

    def set_subject(self, value: str) -> None:
        self.subject = value

    def set_message(self, value: str) -> None:
        self.message = value

    # Submit handler
    async def submit_form(self) -> None:
        if not self.name or not self.email or not self.message:
            self.error = "Please fill in all required fields."
            return

        self.is_submitting = True
        self.error = ""

        try:
            async with get_company_session() as session:
                submission = ContactSubmissionORM(
                    name=self.name,
                    email=self.email,
                    subject=self.subject or None,
                    message=self.message,
                )
                session.add(submission)
                await session.commit()

            self.is_submitted = True
            self.name = ""
            self.email = ""
            self.subject = ""
            self.message = ""
        except (ValueError, RuntimeError) as e:
            self.error = f"Failed to send message: {e}"
        finally:
            self.is_submitting = False

    def reset_form(self) -> None:
        self.is_submitted = False
        self.error = ""
