"""Information cards with error handling."""

import reflex as rx

from ...components.cards import glass_card
from ...components.drawer import CartState
from .state import State
from .dialog import company_profile_dialog


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
            rx.vstack(
                glass_card(
                    rx.text(
                        f"{overview.get('short_name', '')} (Est. {overview.get('established_year', '')})"
                    ),
                    rx.link(website, href=f"https://{website}", is_external=True),
                    rx.text(f"Market cap: {overview.get('market_cap', '')} B. VND"),
                    rx.text(f"Issue Shares: {overview.get('issue_share', '')}"),
                    rx.text(
                        f"Outstanding Shares: {overview.get('outstanding_share', '')}"
                    ),
                    rx.text(
                        f"{overview.get('no_shareholders', '')} shareholders ({overview.get('foreign_percent', '')}% foreign)"
                    ),
                    padding="1em",
                    width="100%",
                ),
                company_profile_dialog(),
                spacing="3",
                width="100%",
            ),
        ),
    )
