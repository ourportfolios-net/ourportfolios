import reflex as rx


def loading_screen():
    """Loading screen that appears while page is not hydrated."""
    return rx.cond(
        rx.State.is_hydrated,
        rx.box(
            rx.box(
                rx.spinner(
                    size="3",
                    color=rx.color("accent", 9),
                ),
                position="fixed",
                bottom="1.5em",
                right="2.5em",
                z_index="1001",
                padding="10px",
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            z_index="1000",
            style={
                "backdropFilter": "blur(3px)",
                "background": "rgba(20, 20, 20, 0.7)",
            },
        ),
    )
