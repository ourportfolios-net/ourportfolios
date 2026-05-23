"""Key metrics card with performance and financial statements tabs."""

from typing import cast

import reflex as rx

from ourportfolios.components.financial_statement import financial_statements
from ourportfolios.pages.ticker_analysis.performance_cards import (
    performance_cards,
)
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.state.framework_state import GlobalFrameworkState
from ourportfolios.ui.primitives import badge, skeleton_box
from ourportfolios.ui.theme import CARD_BORDER, TEXT_PURPLE, purple, white
from ourportfolios.ui.tokens import RADIUS_MD, RADIUS_SM

_CARD_RADIUS = RADIUS_MD

_FRAMEWORK_LINK_STYLE = {
    "backgroundColor": purple(0.1),
    "border": f"1px solid {purple(0.3)}",
    "borderRadius": RADIUS_SM,
    "color": TEXT_PURPLE,
    "transition": "all 0.15s ease",
    "_hover": {
        "backgroundColor": purple(0.18),
        "borderColor": purple(0.45),
    },
}

_SELECT_LINK_STYLE = {
    "backgroundColor": purple(0.12),
    "border": f"1px solid {purple(0.35)}",
    "borderRadius": RADIUS_SM,
    "color": TEXT_PURPLE,
    "transition": "all 0.15s ease",
    "_hover": {
        "backgroundColor": purple(0.22),
        "borderColor": purple(0.5),
    },
}


def _financial_statement_content(
    financial_statement_tabs: list[list[dict[str, str | int | float | None]]],
) -> rx.Component:
    return rx.cond(
        State.is_loading_financial,
        # Skeleton for all three statements while loading
        rx.box(
            rx.vstack(
                *[
                    rx.vstack(
                        skeleton_box(width="11.25rem", height="1.75rem"),
                        skeleton_box(width="100%", height="7.5rem"),
                        spacing="2",
                        width="100%",
                    )
                    for _ in range(3)
                ],
                spacing="6",
                width="100%",
            ),
            width="100%",
            padding_top="0.5em",
            padding_left="0.5em",
            flex="1",
            min_height="0",
            display="flex",
            flex_direction="column",
        ),
        rx.box(
            financial_statements(
                financial_statement_tabs,
                show_skeleton=False,
            ),
            width="100%",
            padding_top="0.5em",
            padding_left="0.5em",
            flex="1",
            min_height="0",
            display="flex",
            flex_direction="column",
        ),
    )


def key_metrics_card():
    financial_statement_tabs = [
        cast("list[dict[str, str | int | float | None]]", State.income_statement),
        cast("list[dict[str, str | int | float | None]]", State.balance_sheet),
        cast("list[dict[str, str | int | float | None]]", State.cash_flow),
    ]

    return rx.box(
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
                            style=_FRAMEWORK_LINK_STYLE,
                        ),
                        href="/framework",
                        underline="none",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.hstack(
                                rx.text("Select a Framework", size="2", weight="bold"),
                                rx.icon("arrow-right", size=12),
                                spacing="1",
                                align="center",
                                padding="0.3em 0.6em",
                                style=_SELECT_LINK_STYLE,
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
                    rx.cond(
                        State.switch_value == "quarter",
                        badge("Quarterly", color_variant="purple"),
                        badge("Quarterly", color_variant="gray"),
                    ),
                    rx.switch(
                        checked=State.switch_value == "year",
                        on_change=State.toggle_switch,
                    ),
                    rx.cond(
                        State.switch_value == "year",
                        badge("Yearly", color_variant="purple"),
                        badge("Yearly", color_variant="gray"),
                    ),
                    justify="center",
                    align="center",
                    spacing="2",
                    flex_shrink="0",
                ),
                width="100%",
                align="center",
                spacing="3",
                flex_wrap="wrap",
                flex_shrink="0",
            ),
            rx.tabs.content(
                rx.box(
                    performance_cards(),
                    flex="1",
                    overflow_y="auto",
                ),
                value="performance",
                padding_top="1em",
                flex="1",
                min_height="0",
                display="flex",
                flex_direction="column",
            ),
            rx.tabs.content(
                rx.box(
                    rx.box(
                        rx.scroll_area(
                            rx.box(
                                _financial_statement_content(
                                    financial_statement_tabs,
                                ),
                                width="max-content",
                            ),
                            scrollbars="horizontal",
                            type="hover",
                        ),
                        display=["block", "block", "none"],
                        width="100%",
                        padding_left="1rem",
                    ),
                    rx.box(
                        _financial_statement_content(financial_statement_tabs),
                        width="100%",
                        flex="1",
                        min_height="0",
                        overflow_y="auto",
                        display=["none", "none", "flex"],
                        flex_direction="column",
                    ),
                    flex="1",
                    display="flex",
                    flex_direction="column",
                ),
                value="statement",
                padding_top="1em",
                flex="1",
                min_height="0",
                display="flex",
                flex_direction="column",
            ),
            value=State.selected_tab,
            on_change=State.set_selected_tab,
            width="100%",
            flex="1",
            display="flex",
            flex_direction="column",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1.25rem",
        flex="2",
        width="100%",
        min_width="0",
        max_width="100%",
        height="100%",
        display="flex",
        flex_direction="column",
        overflow="hidden",
    )
