import reflex as rx
from ...state.auth_state import AuthState
from ...styles import purple, TEXT_TERTIARY


@rx.page(route="/auth/callback", on_load=AuthState.handle_oauth_callback)
def callback() -> rx.Component:
    return rx.box(
        rx.box(
            position="absolute",
            top="-20rem",
            left="50%",
            transform="translateX(-50%)",
            width="40rem",
            height="40rem",
            background=f"radial-gradient(circle, {purple(0.05)} 0%, transparent 70%)",
            pointer_events="none",
            z_index="0",
        ),
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Signing you in...", size="2", color=TEXT_TERTIARY),
            spacing="4",
            align="center",
            position="absolute",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            z_index="1",
        ),
        background="#090909",
        color="white",
        min_height="100vh",
        width="100%",
        position="relative",
        overflow="hidden",
    )
