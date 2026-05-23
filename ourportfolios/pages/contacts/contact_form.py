import reflex as rx

from ourportfolios.pages.auth.components import (
    INPUT_OVERRIDE,
    action_button,
    label,
    text_input,
)
from ourportfolios.state.contact_state import ContactState
from ourportfolios.ui.primitives import heading, muted_text
from ourportfolios.ui.theme import TEXT_PRIMARY, TEXT_TERTIARY, white
from ourportfolios.ui.tokens import RADIUS_SM

# ── Intent chip selector state ─────────────────────────────────────────────


class ContactIntentState(rx.State):
    selected: rx.Field[str] = rx.field(default="")

    @rx.event
    def pick(self, intent: str) -> None:
        self.selected = intent


# ── Form sub-components ────────────────────────────────────────────────────


def _name_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            label("First Name"),
            text_input(
                "Our",
                ContactState.first_name,
                ContactState.set_first_name,
                "text",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            label("Last Name"),
            text_input(
                "Portfolios",
                ContactState.last_name,
                ContactState.set_last_name,
                "text",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        spacing="3",
        width="100%",
        flex_direction=["column", "row"],
    )


def _email_field() -> rx.Component:
    return rx.vstack(
        label("Email"),
        text_input(
            "op@example.com",
            ContactState.email,
            ContactState.set_email,
            "email",
        ),
        spacing="0",
        width="100%",
        align="start",
    )


def _subject_field() -> rx.Component:
    return rx.vstack(
        label("Subject"),
        text_input(
            "What's this about?",
            ContactState.subject,
            ContactState.set_subject,
            "text",
        ),
        spacing="0",
        width="100%",
        align="start",
    )


def _message_field() -> rx.Component:
    return rx.vstack(
        label("Message"),
        rx.text_area(
            placeholder="Tell us more…",
            value=ContactState.message,
            on_change=ContactState.set_message,
            style={
                **INPUT_OVERRIDE,
                "min_height": "9rem",
                "max_height": "24rem",  # Sets the expansion limit
                "padding_y": "0.75rem",
                "resize": "vertical",  # Allows vertical expansion
            },
        ),
        spacing="0",
        width="100%",
        align="start",
    )


def _error_text() -> rx.Component:
    return rx.cond(
        ContactState.error != "",
        rx.text(ContactState.error, size="1", color="rgba(255, 100, 100, 0.8)"),
        rx.fragment(),
    )


def _form_fields() -> rx.Component:
    return rx.vstack(
        _name_row(),
        _email_field(),
        _subject_field(),
        _message_field(),
        _error_text(),
        spacing="4",
        width="100%",
    )


def _submit_button() -> rx.Component:
    return action_button(
        "Send message",
        ContactState.submit,
        loading=ContactState.is_submitting,
        loading_label="Sending…",
    )


def contact_form() -> rx.Component:
    return rx.vstack(
        _form_fields(),
        _submit_button(),
        spacing="4",
        width="100%",
        align="start",
    )


def contact_success() -> rx.Component:
    return rx.vstack(
        rx.icon("check_check", size=32, color=white(0.6)),
        heading("Message sent!", level=2, color=TEXT_PRIMARY),
        muted_text(
            "We'll get back to you as soon as possible.",
            size="2",
            color=TEXT_TERTIARY,
            text_align="center",
        ),
        action_button(
            "Send another",
            ContactState.reset_form,
            loading=False,
            loading_label="",
        ),
        spacing="2",
        align="center",
        width="100%",
    )


# ── Left column: marketing content ──────────────────────────────────────────


def _hero_text() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Let's connect",
            font_size=["2.5rem", "3.5rem"],
            font_weight="750",
            color=TEXT_PRIMARY,
            line_height="1.1",
            letter_spacing="-0.04em",
        ),
        rx.text(
            "Have a question, feedback, or want to collaborate?",
            font_size=["0.875rem", "1rem"],
            color=TEXT_TERTIARY,
            line_height="1.6",
        ),
        spacing="4",
        align="start",
        width="100%",
    )


_INTENTS: list[tuple[str, str, str, str]] = [
    (
        "message-circle",
        "Quick question",
        "Question regarding...",
        "Hi team!\n\nI was browsing through the platform and was curious about [Topic]. Specifically, I wanted to know...",
    ),
    (
        "lightbulb",
        "Feature request",
        "Idea for the platform",
        "I've been using the platform and thought this would be a cool addition:\n\n[Describe feature]\n\nIt would be helpful because...",
    ),
    (
        "sparkles",
        "Let's team up",
        "Collaboration inquiry",
        "Hey! I'm [Name/Role] and I'm working on [Project]. I think there's some cool overlap with what you're building. Would love to chat about...",
    ),
    (
        "hammer",
        "Something's broken",
        "Bug report",
        "I ran into a snag. Here is what happened:\n\n1. I went to...\n2. I clicked...\n\nExpected: [Behavior]\nActual: [What happened]",
    ),
    (
        "thumbs-up",
        "General feedback",
        "Feedback on ourportfolios",
        "Just wanted to share some thoughts on the site. I really like [X], but I found [Y] a bit confusing because...",
    ),
]


def _intent_chip(
    icon_name: str,
    label_text: str,
    subject_text: str,
    message_text: str,
) -> rx.Component:
    is_selected = ContactIntentState.selected == label_text
    return rx.box(
        rx.hstack(
            rx.icon(icon_name, size=16),
            rx.text(label_text, size="2", weight="medium"),
            spacing="2",
            align="center",
        ),
        on_click=[
            ContactIntentState.pick(label_text),
            ContactState.set_subject(subject_text),
            ContactState.set_message(message_text),
        ],
        cursor="pointer",
        padding="0.45rem 0.85rem",
        border_radius=RADIUS_SM,
        border=rx.cond(
            is_selected,
            f"1px solid {white(0.25)}",
            f"1px solid {white(0.08)}",
        ),
        background=rx.cond(is_selected, white(0.08), white(0.03)),
        color=rx.cond(is_selected, white(0.9), white(0.45)),
        transition="all 0.15s ease",
        _hover={
            "background": white(0.07),
            "border_color": white(0.18),
            "color": white(0.8),
        },
        user_select="none",
    )


def _intent_selector() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Start with a message template",
            size="2",
            color=white(0.3),
            weight="medium",
            letter_spacing="0.02em",
        ),
        rx.flex(
            *[_intent_chip(icon, lbl, sub, msg) for icon, lbl, sub, msg in _INTENTS],
            gap="0.5rem",
            flex_wrap="wrap",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def marketing_column() -> rx.Component:
    return rx.vstack(
        _hero_text(),
        rx.spacer(),
        _intent_selector(),
        spacing="0",
        align="start",
        width="100%",
        height="100%",
    )
