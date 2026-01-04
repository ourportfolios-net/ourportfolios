import reflex as rx
from ourportfolios.pages import (  # noqa: F401
    landing,
    recommend,
    select,
    ticker_analysis,
    industry_analysis,
    analyze,
    compare,
)

app = rx.App(
    style={"font_family": "Outfit"},
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap"
    ],
    theme=rx.theme(accent_color="violet"),
)
