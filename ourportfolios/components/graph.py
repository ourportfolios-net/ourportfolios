import reflex as rx


def mini_price_graph(label, data, diff, size=(80, 40)):
    width, height = size
    return rx.vstack(
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="normalized_close",
                stroke=rx.color("accent", 9),
                fill=rx.color("accent", 8),
            ),
            rx.recharts.x_axis(data_key="name", hide=True),
            rx.recharts.y_axis(domain=[0, 1], hide=True),
            data=data,
            width=width,
            height=height,
        ),
        rx.hstack(
            rx.text(label, size="1", font_size="0.75rem"),
            pct_change_badge(diff=diff),
        ),
        spacing="1",
        align="center",
        justify="center",
    )


def pct_change_badge(diff: float):
    diff = diff.to(float)  # Convert to Python[float]
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
            rx.text(f"{diff:.2f}%", size="1", weight="medium"),
            spacing="1",
            align="center",
            justify="center",
        ),
        color_scheme=color_scheme,
        size="1",
        style={"padding": "0.1em 0.3em"},
        height="1.55vw",
    )
