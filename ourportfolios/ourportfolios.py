import reflex as rx

from ourportfolios import pages

app = rx.App(
    style={"font_family": "Outfit"},
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap",
    ],
    theme=rx.theme(accent_color="violet"),
)

__all__ = ["pages"]
