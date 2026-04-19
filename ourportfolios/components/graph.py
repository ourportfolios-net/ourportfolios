import reflex as rx


def pct_change_badge(diff: float):
    color_scheme = rx.cond(diff > 0, "green", rx.cond(diff < 0, "red", "gray"))

    return rx.badge(
        rx.flex(
            rx.cond(
                diff > 0,
                rx.icon(tag="arrow_up", size=12),
                rx.cond(
                    diff < 0,
                    rx.icon(tag="arrow_down", size=12),
                    rx.icon(tag="minus", size=12),
                ),
            ),
            rx.hstack(
                rx.cond(
                    diff > 0, rx.text("+", size="1", weight="medium"), rx.fragment(),
                ),
                rx.text(diff, size="1", weight="medium"),
                rx.text("%", size="1", weight="medium"),
                spacing="0",
                align="center",
            ),
            spacing="1",
            align="center",
            justify="center",
        ),
        color_scheme=color_scheme,
        size="1",
        padding="0.1em 0.3em",
        height="1.55vw",
    )
