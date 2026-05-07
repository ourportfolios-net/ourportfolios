"""Contact form components built with shared auth UI primitives."""

import reflex as rx

from ourportfolios.pages.auth.components import (
    INPUT_OVERRIDE,
    action_btn,
    label,
    text_input,
)
from ourportfolios.state.contact import ContactState
from ourportfolios.styles import (
    TEXT_PRIMARY,
    TEXT_TERTIARY,
    white,
)


def _name_row() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            label("First name"),
            text_input(
                "Jane",
                ContactState.first_name,
                ContactState.set_first_name,
                "text",
            ),
            spacing="0",
            width="100%",
            align="start",
        ),
        rx.vstack(
            label("Last name"),
            text_input(
                "Smith",
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
        label("Email address"),
        text_input(
            "you@example.com",
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
                "height": "9rem",
                "padding_y": "0.75rem",
                "resize": "none",
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
    return action_btn(
        "Send message",
        ContactState.submit,
        loading=ContactState.is_submitting,
        loading_label="Sending…",
    )


def contact_form() -> rx.Component:
    """Render the form fields + submit button."""
    return rx.vstack(
        _form_fields(),
        _submit_button(),
        spacing="4",
        width="100%",
        align="start",
    )


def contact_success() -> rx.Component:
    """Success state — shown after form submission."""
    return rx.vstack(
        rx.text(
            "✓",
            font_size="2rem",
            font_weight="700",
            color=white(0.6),
        ),
        rx.text(
            "Message sent!",
            font_size="1.4rem",
            font_weight="700",
            color=TEXT_PRIMARY,
        ),
        rx.text(
            "We'll get back to you as soon as possible.",
            size="2",
            color=TEXT_TERTIARY,
            text_align="center",
        ),
        action_btn(
            "Send another",
            ContactState.reset_form,
            loading=False,
            loading_label="",
        ),
        spacing="3",
        align="center",
        padding_y="1rem",
        width="100%",
    )


# ── Left column: marketing content ──────────────────────────────────


def _hero_text() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Let's connect",
            font_size=["2.5rem", "3.5rem"],
            font_weight="800",
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


def _steps() -> rx.Component:
    items = [
        ("1", "Send us a message using the form"),
        ("2", "We review and route it to the right person"),
        ("3", "We'll follow up with next steps"),
    ]
    return rx.vstack(
        *[
            rx.hstack(
                rx.box(
                    rx.text(
                        num,
                        font_size="0.75rem",
                        font_weight="700",
                        color=white(0.7),
                    ),
                    background=white(0.05),
                    border_radius="0.375rem",
                    width="1.5rem",
                    height="1.5rem",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    flex_shrink="0",
                ),
                rx.text(
                    text,
                    size="2",
                    color=white(0.5),
                    line_height="1.5",
                ),
                spacing="3",
                align="center",
                width="100%",
            )
            for num, text in items
        ],
        spacing="3",
        align="start",
        width="100%",
    )


def _fun_footer() -> rx.Component:
    """Creative footer text at bottom left of marketing column."""
    return rx.vstack(
        rx.text(
            "P.S. We're real people, promise — no bots here (except the trading ones).",
            size="2",
            color=white(0.35),
            line_height="1.5",
        ),
        spacing="0",
        align="start",
        width="100%",
        margin_top="4",
    )


def marketing_column() -> rx.Component:
    """Left column content for the two-column layout."""
    return rx.vstack(
        _hero_text(),
        _steps(),
        _fun_footer(),
        spacing="8",
        align="start",
        width="100%",
        max_width="28rem",
    )
