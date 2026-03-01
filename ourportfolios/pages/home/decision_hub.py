import reflex as rx
from .hub_cards import compare_assets_card, manage_portfolio_card
from .framework_card import select_framework_card


def decision_hub_section() -> rx.Component:
    return rx.grid(
        select_framework_card(),
        compare_assets_card(),
        manage_portfolio_card(),
        columns=rx.breakpoints(initial="1", md="3", lg="3"),
        gap="1.25rem",
        width="100%",
    )
