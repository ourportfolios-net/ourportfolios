"""Key metrics card with performance and financial statements tabs."""

from typing import cast

import reflex as rx

from ourportfolios.components.financial_statement import financial_statements
from ourportfolios.pages.ticker_analysis.performance_cards import performance_cards
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.state.framework_state import GlobalFrameworkState
from ourportfolios.styles import CARD_BORDER, TEXT_PURPLE, purple, white

_CARD_RADIUS = "0.625rem"


def key_metrics_card():
    financial_statement_tabs = [
        cast("list[dict[str, str | int | float | None]]", State.income_statement),
        cast("list[dict[str, str | int | float | None]]", State.balance_sheet),
        cast("list[dict[str, str | int | float | None]]", State.cash_flow),
    ]

    return rx.box(
        rx.vstack(
            rx.tabs.root(
                rx.hstack(
                    # Tabs on the left
                    rx.tabs.list(
                        rx.tabs.trigger("Performance", value="performance"),
                        rx.tabs.trigger("Financial Statements", value="statement"),
                        flex_shrink="0",
                    ),
                    rx.spacer(),
                    # Framework indicator inline with tabs
                    rx.cond(
                        GlobalFrameworkState.has_selected_framework,
                        rx.link(
                            rx.hstack(
                                rx.icon("target", size=13),
                                rx.text(
                                    GlobalFrameworkState.framework_display_name,
                                    size="2",
                                    weight="medium",
                                    white_space="nowrap",
                                ),
                                rx.icon("external-link", size=11),
                                spacing="2",
                                align="center",
                                padding="0.35em 0.65em",
                                style={
                                    "backgroundColor": purple(0.1),
                                    "border": f"1px solid {purple(0.3)}",
                                    "borderRadius": "0.375rem",
                                    "color": TEXT_PURPLE,
                                    "transition": "all 0.15s ease",
                                    "_hover": {
                                        "backgroundColor": purple(0.18),
                                        "borderColor": purple(0.45),
                                    },
                                },
                            ),
                            href="/framework",
                            underline="none",
                        ),
                        rx.hstack(
                            rx.icon("target", size=13, color=white(0.35)),
                            rx.text(
                                "No framework selected.",
                                size="2",
                                color=white(0.45),
                                white_space="nowrap",
                            ),
                            rx.link(
                                rx.hstack(
                                    rx.icon("arrow-right", size=12),
                                    rx.text("Select", size="2", weight="bold"),
                                    spacing="1",
                                    align="center",
                                    padding="0.3em 0.6em",
                                    style={
                                        "backgroundColor": purple(0.12),
                                        "border": f"1px solid {purple(0.35)}",
                                        "borderRadius": "0.375rem",
                                        "color": TEXT_PURPLE,
                                        "transition": "all 0.15s ease",
                                        "_hover": {
                                            "backgroundColor": purple(0.22),
                                            "borderColor": purple(0.5),
                                        },
                                    },
                                ),
                                href="/framework",
                                underline="none",
                            ),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    # Quarterly / Yearly toggle on the far right
                    rx.hstack(
                        rx.badge(
                            "Quarterly",
                            color_scheme=rx.cond(
                                State.switch_value == "quarter",
                                "violet",
                                "gray",
                            ),
                            variant="soft",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        rx.switch(
                            checked=State.switch_value == "year",
                            on_change=State.toggle_switch,
                        ),
                        rx.badge(
                            "Yearly",
                            color_scheme=rx.cond(
                                State.switch_value == "year",
                                "violet",
                                "gray",
                            ),
                            variant="soft",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        justify="center",
                        align="center",
                        spacing="2",
                        flex_shrink="0",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                    style={"flexWrap": "wrap"},
                ),
                rx.tabs.content(
                    performance_cards(),
                    value="performance",
                    padding_top="1em",
                ),
                rx.tabs.content(
                    rx.cond(
                        State.is_loading_financial,
                        # Skeleton for all three statements while loading
                        rx.box(
                            rx.vstack(
                                *[
                                    rx.vstack(
                                        rx.skeleton(
                                            rx.box(height="1.75rem", width="11.25rem"),
                                            loading=True,
                                            style={"border_radius": "0.375rem"},
                                        ),
                                        rx.skeleton(
                                            rx.box(height="7.5rem", width="100%"),
                                            loading=True,
                                            style={"border_radius": "0.375rem"},
                                        ),
                                        spacing="2",
                                        width="100%",
                                    )
                                    for _ in range(3)
                                ],
                                spacing="6",
                                width="100%",
                            ),
                            width="100%",
                            padding_top="2em",
                            padding_left="0.5em",
                        ),
                        rx.box(
                            financial_statements(
                                financial_statement_tabs, show_skeleton=False,
                            ),
                            width="100%",
                            padding_top="2em",
                            padding_left="0.5em",
                            style={"display": "block", "textAlign": "left"},
                        ),
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
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1rem",
        flex="2",
        width="100%",
        min_width="0",
        max_width="100%",
        overflow="hidden",
    )
