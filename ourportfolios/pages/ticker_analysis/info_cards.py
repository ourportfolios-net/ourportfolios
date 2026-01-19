"""Information cards with error handling."""

import reflex as rx

from ...components.cards import glass_card
from ...components.drawer import CartState
from .state import State


def name_card_skeleton():
    """Skeleton for the name card"""
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.skeleton(height="3rem", width="8rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="2rem", border_radius="14px"),
                justify="center",
                align="center",
            ),
            rx.hstack(
                rx.skeleton(height="1.5rem", width="4rem", border_radius="14px"),
                rx.skeleton(height="1.5rem", width="6rem", border_radius="14px"),
                spacing="2",
            ),
            spacing="3",
            align="center",
        ),
        style={"width": "100%", "padding": "1em"},
    )


def error_card(message: str):
    """Generic error card"""
    return glass_card(
        rx.vstack(
            rx.icon("triangle-alert", size=32, color="tomato"),
            rx.text(
                "Failed to load data",
                size="4",
                weight="bold",
                color="tomato",
            ),
            rx.text(
                message,
                size="2",
                color="gray",
                text_align="center",
            ),
            spacing="2",
            align="center",
        ),
        style={"width": "100%", "padding": "2em"},
    )


def general_info_card_skeleton():
    """Simplified skeleton for the general info card"""
    return glass_card(
        rx.skeleton(height="10rem", width="100%", border_radius="14px"),
        style={"width": "100%", "padding": "1em"},
    )


def company_profile_skeleton():
    """Skeleton for the company profile card"""
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.skeleton(height="2rem", width="8rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="6rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="7rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="5rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="9rem", border_radius="14px"),
                rx.skeleton(height="2rem", width="7rem", border_radius="14px"),
                spacing="2",
            ),
            rx.skeleton(height="12em", width="100%", border_radius="14px"),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="1em",
    )


def name_card():
    overview = State.overview

    return rx.cond(
        State.is_loading_company,
        name_card_skeleton(),
        rx.cond(
            State.error_company != "",
            error_card(State.error_company),
            glass_card(
                rx.vstack(
                    rx.hstack(
                        rx.heading(overview.get("symbol", ""), size="9"),
                        rx.button(
                            rx.icon("plus", size=16),
                            size="2",
                            variant="soft",
                            on_click=lambda: CartState.add_item(
                                overview.get("symbol", "")
                            ),
                        ),
                        justify="center",
                        align="center",
                    ),
                    rx.hstack(
                        rx.badge(f"{overview.get('exchange', '')}", variant="surface"),
                        rx.badge(f"{overview.get('industry', '')}"),
                    ),
                ),
                padding="1em",
                width="100%",
            ),
        ),
    )


def general_info_card():
    overview = State.overview
    website = overview.get("website", "")

    return rx.cond(
        State.is_loading_company,
        general_info_card_skeleton(),
        rx.cond(
            State.error_company != "",
            error_card(State.error_company),
            glass_card(
                rx.text(
                    f"{overview.get('short_name', '')} (Est. {overview.get('established_year', '')})"
                ),
                rx.link(website, href=f"https://{website}", is_external=True),
                rx.text(f"Market cap: {overview.get('market_cap', '')} B. VND"),
                rx.text(f"Issue Shares: {overview.get('issue_share', '')}"),
                rx.text(f"Outstanding Shares: {overview.get('outstanding_share', '')}"),
                rx.text(
                    f"{overview.get('no_shareholders', '')} shareholders ({overview.get('foreign_percent', '')}% foreign)"
                ),
                padding="1em",
                width="100%",
            ),
        ),
    )


def company_profile_card():
    profile_data = State.profile
    PROFILE_CONTENT_HEIGHT = "12em"

    def create_profile_tab_content(content_key: str, tab_value: str):
        return rx.tabs.content(
            rx.scroll_area(
                rx.text(
                    profile_data.get(content_key, ""),
                    size="3",
                    weight="regular",
                    style={
                        "whiteSpace": "pre-wrap",
                        "wordWrap": "break-word",
                        "textAlign": "justify",
                        "lineHeight": "1.6",
                    },
                ),
                height=PROFILE_CONTENT_HEIGHT,
                padding="0.5em",
            ),
            value=tab_value,
            padding_top="0.8em",
        )

    return rx.cond(
        State.is_loading_company,
        company_profile_skeleton(),
        rx.cond(
            State.error_company != "",
            error_card(State.error_company),
            glass_card(
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Company Profile", value="profile"),
                        rx.tabs.trigger("History", value="history"),
                        rx.tabs.trigger("Promises", value="promises"),
                        rx.tabs.trigger("Risks", value="risks"),
                        rx.tabs.trigger("Developments", value="developments"),
                        rx.tabs.trigger("Strategies", value="strategies"),
                        variant="surface",
                    ),
                    create_profile_tab_content("company_profile", "profile"),
                    create_profile_tab_content("history_dev", "history"),
                    create_profile_tab_content("company_promise", "promises"),
                    create_profile_tab_content("business_risk", "risks"),
                    create_profile_tab_content("key_developments", "developments"),
                    create_profile_tab_content("business_strategies", "strategies"),
                    default_value="profile",
                ),
                width="100%",
                padding="1em",
            ),
        ),
    )
