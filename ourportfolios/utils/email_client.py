"""Email client for sending contact form emails via Resend templates."""

import contextlib
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", "")
_RESEND_AVAILABLE: bool = bool(_RESEND_API_KEY)

if _RESEND_AVAILABLE:
    import resend

    resend.api_key = _RESEND_API_KEY


@dataclass
class EmailConfig:
    contact_template_id: str
    thankyou_template_id: str
    from_email: str
    to_email: str


def load_email_config() -> EmailConfig:
    """Load email configuration from environment variables."""
    to_email = os.environ.get("CONTACT_TO_EMAIL", "")
    return EmailConfig(
        contact_template_id=os.environ.get("TEMPLATE_CONTACT_ID", ""),
        thankyou_template_id=os.environ.get(
            "TEMPLATE_THANKYOU_ID", "contact-auto-reply",
        ),
        from_email=os.environ.get("CONTACT_FROM_EMAIL", to_email),
        to_email=to_email,
    )


async def send_contact_emails(  # noqa: PLR0913
    first: str,
    last: str,
    sender_email: str,
    subject: str,
    message: str,
    config: EmailConfig,
) -> tuple[bool, str]:
    """Send contact form emails using Resend templates.

    Sends two emails:
    1. Notification to the site owner (config.to_email)
    2. Thank-you email to the user (sender_email)
    """
    if not _RESEND_AVAILABLE:
        return False, "Email service is not configured. Please try again later."

    success = True
    error_msg = ""

    if config.contact_template_id:
        try:
            resend.Emails.send(
                {
                    "from": config.from_email,
                    "to": [config.to_email],
                    "reply_to": [sender_email],
                    "subject": subject or "Contact Form Submission",
                    "template": {
                        "id": config.contact_template_id,
                        "variables": {
                            "first_name": first,
                            "last_name": last,
                            "email": sender_email,
                            "subject": subject or "(No subject)",
                            "message": message,
                        },
                    },
                },
            )
        except Exception as e:  # noqa: BLE001
            success = False
            error_msg = f"Failed to send notification: {e}"

    if config.thankyou_template_id:
        with contextlib.suppress(Exception):
            resend.Emails.send(
                {
                    "from": config.from_email,
                    "to": [sender_email],
                    "subject": "Thank you for contacting us",
                    "template": {
                        "id": config.thankyou_template_id,
                        "variables": {
                            "name": first or "there",
                            "subject": subject or "(No subject)",
                        },
                    },
                },
            )

    return success, error_msg
