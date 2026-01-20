import reflex as rx
from ...state.home_state import HomeState
from .decision_hub_card import decision_hub_card
from .framework_card import select_framework_card
from .portfolio_card import portfolio_card_with_hover


def decision_hub_section():
    """Create the decision hub section."""
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "Decision Hub", size="8", font_weight="800", letter_spacing="-0.02em"
            ),
            rx.text(
                "Select a primary workflow to begin your market analysis.",
                color="rgba(255, 255, 255, 0.4)",
                font_weight="500",
            ),
            spacing="2",
            align="start",
        ),
        rx.grid(
            select_framework_card(),
            decision_hub_card(
                title="Compare Assets",
                description="Side-by-side performance benchmarking and correlation analysis between multiple tickers or indices.",
                icon="git-compare",
                color="blue",
                button_text="Start Comparison",
                button_variant="outline",
                on_click=HomeState.handle_compare,
                has_comparison_chart=True,
            ),
            portfolio_card_with_hover(),
            columns=rx.breakpoints(initial="1", md="2", lg="3"),
            gap="1rem",
            width="100%",
        ),
        spacing="6",
        width="100%",
        align="start",
    )
