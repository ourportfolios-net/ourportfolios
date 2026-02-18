import reflex as rx
from ...state.home_state import HomeState
from .decision_hub_card import decision_hub_card
from .framework_card import select_framework_card
from .portfolio_card import portfolio_card_with_hover


def decision_hub_section():
    """Create the decision hub cards grid."""
    return rx.grid(
        select_framework_card(),
        rx.box(
            decision_hub_card(
                title="Compare Assets",
                description="Head-to-head metrics. Analyze P/E, EPS, and Volatility side-by-side.",
                icon="git-compare",
                color="blue",
                button_text="Go to Comparison",
                button_variant="outline",
                on_click=HomeState.handle_compare,
                has_comparison_chart=True,
            ),
            on_mouse_enter=HomeState.start_comparison_hover,
            on_mouse_leave=HomeState.end_comparison_hover,
        ),
        portfolio_card_with_hover(),
        columns=rx.breakpoints(initial="1", md="3", lg="3"),
        gap="1.25rem",
        width="100%",
    )
