"""Contacts page — two-column Neon-style layout with navbar and footer."""

import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.pages.auth.components import (
    auth_page_shell,
)
from ourportfolios.pages.contacts.contact_form import (
    contact_form,
    contact_success,
    marketing_column,
)
from ourportfolios.pages.landing.sections.footer import footer
from ourportfolios.state.contact import ContactState
from ourportfolios.styles import white


def _form_card() -> rx.Component:
    """Right column — the contact form card."""
    return rx.box(
        # Purple blob at top of form
        rx.box(
            position="absolute",
            top="-2rem",
            left="-2rem",
            width="20rem",
            height="20rem",
            background=f"radial-gradient(ellipse at 50% 50%, {white(0.03)} 0%, transparent 70%)",
            pointer_events="none",
        ),
        rx.cond(
            ContactState.submitted,
            contact_success(),
            contact_form(),
        ),
        background="rgba(255, 255, 255, 0.03)",
        border=f"1px solid {white(0.06)}",
        border_radius="1rem",
        padding=rx.breakpoints(initial="1.5rem", sm="2.5rem"),
        width="100%",
        max_width="32rem",
        position="relative",
    )


@rx.page(route="/contacts")
def contact_page() -> rx.Component:
    return auth_page_shell(
        navbar(),
        rx.box(
            rx.center(
                rx.box(
                    rx.hstack(
                        # Left column — marketing content
                        rx.box(
                            marketing_column(),
                            flex="1",
                            min_width="0",
                        ),
                        # Right column — form
                        rx.box(
                            _form_card(),
                            flex="1",
                            min_width="0",
                        ),
                        spacing="8",
                        align="start",
                        flex_direction=["column", "row"],
                        width="100%",
                    ),
                    width="100%",
                    max_width="86vw",
                ),
                width="100%",
                padding_x=rx.breakpoints(initial="1.5rem", sm="3rem"),
                padding_y=rx.breakpoints(initial="3rem", sm="6rem"),
                min_height="calc(100vh - 4rem)",
            ),
        ),
        footer(),
    )
