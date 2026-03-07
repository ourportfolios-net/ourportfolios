import reflex as rx
from .hub_cards import compare_assets_card, manage_portfolio_card
from .framework_card import select_framework_card


def decision_hub_section() -> rx.Component:
    return rx.box(
        select_framework_card(),
        compare_assets_card(),
        manage_portfolio_card(),
        display="grid",
        grid_template_columns="repeat(auto-fill, minmax(min(18rem, 100%), 1fr))",
        gap="1.25rem",
        width="100%",
    )
