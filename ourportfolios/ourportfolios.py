import reflex as rx

# MUST BE IMPORTED!!!
from ourportfolios.pages import (
    landing,
    recommend,
    select,
    ticker_analysis,
    industry_analysis,
    analyze,
    compare,
)  # noqa: F401


app = rx.App(
    style={"font_family": "Outfit"},
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap"
    ],
    theme=rx.theme(accent_color="violet"),
)
