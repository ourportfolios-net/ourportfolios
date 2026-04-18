import reflex as rx

from ourportfolios.pages.home.components.hub_cards import (
    compare_assets_card,
    manage_portfolio_card,
    select_framework_card,
)


def decision_hub_section() -> rx.Component:
    return rx.box(
        select_framework_card(),
        compare_assets_card(),
        manage_portfolio_card(),
        display="grid",
        grid_template_columns=rx.breakpoints(
            initial="1fr",
            sm="repeat(3, minmax(0, 1fr))",
        ),
        gap=rx.breakpoints(initial="0.875rem", sm="1.25rem"),
        width="100%",
    )
