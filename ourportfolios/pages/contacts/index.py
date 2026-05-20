import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.pages.auth.components import auth_page_shell
from ourportfolios.pages.contacts.contact_form import (
    contact_form,
    contact_success,
    marketing_column,
)
from ourportfolios.pages.landing.sections.footer import footer
from ourportfolios.state.contact_state import ContactState
from ourportfolios.ui.primitives import surface_box


def _form_card() -> rx.Component:
    return surface_box(
        rx.cond(
            ContactState.submitted,
            contact_success(),
            contact_form(),
        ),
        padding=rx.breakpoints(initial="1.5rem", sm="2.5rem"),
        width="100%",
        position="relative",
    )


@rx.page(route="/contacts")
def index() -> rx.Component:
    return auth_page_shell(
        navbar(),
        rx.box(
            rx.box(
                rx.box(
                    marketing_column(),
                    height="100%",
                    display="flex",
                    flex_direction="column",
                ),
                # Right column wrapper containing the top blob and the form
                rx.box(
                    rx.box(
                        position="absolute",
                        # left="50%",
                        transform="translateX(-200%)",
                        width="22rem",
                        background="radial-gradient(ellipse at 50% 100%, rgba(139, 92, 246, 0.15) 0%, transparent 70%)",
                        pointer_events="none",
                        z_index="0",
                    ),
                    rx.box(
                        _form_card(),
                        position="relative",
                        z_index="1",
                        width="100%",
                    ),
                    position="relative",
                    width="100%",
                ),
                display="grid",
                grid_template_columns=rx.breakpoints(
                    initial="1fr",
                    sm="1fr 32rem",
                ),
                gap=rx.breakpoints(initial="1rem", sm="4rem"),
                align_items="center",
                width="77vw",
                margin="0 auto",
            ),
            width="100%",
            padding_y=rx.breakpoints(initial="3rem", sm="6rem"),
            min_height="calc(100vh - 4rem)",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        footer(),
    )
