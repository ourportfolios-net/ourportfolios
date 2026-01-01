"""Key metrics card with performance and financial statements tabs."""

import reflex as rx

from ...components.financial_statement import financial_statements
from .state import State
from .performance_cards import performance_cards, framework_indicator


def key_metrics_card():
    return rx.card(
        rx.vstack(
            rx.tabs.root(
                rx.hstack(
                    framework_indicator(),
                    rx.tabs.list(
                        rx.tabs.trigger("Performance", value="performance"),
                        rx.tabs.trigger("Financial Statements", value="statement"),
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.badge(
                            "Quarterly",
                            color_scheme=rx.cond(
                                State.switch_value == "quarter", "accent", "gray"
                            ),
                        ),
                        rx.switch(
                            checked=State.switch_value == "year",
                            on_change=State.toggle_switch,
                        ),
                        rx.badge(
                            "Yearly",
                            color_scheme=rx.cond(
                                State.switch_value == "year", "accent", "gray"
                            ),
                        ),
                        justify="center",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.tabs.content(
                    performance_cards(),
                    value="performance",
                    padding_top="1em",
                ),
                rx.tabs.content(
                    rx.box(
                        financial_statements(
                            [
                                State.income_statement,
                                State.balance_sheet,
                                State.cash_flow,
                            ],
                            show_skeleton=State.is_loading_financial,
                        ),
                        width="100%",
                        padding_top="2em",
                        padding_left="0.5em",
                        style={
                            "display": "block",
                            "textAlign": "left",
                        },
                    ),
                    value="statement",
                    padding_top="1em",
                ),
                default_value="performance",
                width="100%",
            ),
            spacing="0",
            justify="center",
            width="100%",
        ),
        padding="1em",
        flex=2,
        width="100%",
        min_width=0,
        max_width="100%",
    )
