"""Information cards with error handling."""

import reflex as rx

from ...components.drawer import CartState
from ...styles import white, CARD_BORDER
from .state import State
from .dialog import company_profile_dialog

_CARD_RADIUS = "10px"


def _skel(w: str, h: str) -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        style={"border_radius": "6px"},
    )


def name_card_skeleton():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.skeleton(
                    rx.box(width="31px", height="31px"),
                    loading=True,
                    style={"border_radius": "8px"},
                ),
                rx.spacer(),
                _skel("70px", "18px"),
                width="100%",
                align="center",
            ),
            rx.vstack(
                _skel("55%", "36px"),
                rx.hstack(
                    _skel("60px", "22px"),
                    _skel("80px", "22px"),
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1.25rem",
        width="100%",
    )


def general_info_card_skeleton():
    return rx.box(
        rx.vstack(
            *[_skel("90%", "14px") for _ in range(5)],
            spacing="2",
            width="100%",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1.25rem",
        width="100%",
    )


def error_card(message: str):
    return rx.box(
        rx.vstack(
            rx.icon("triangle-alert", size=28, color="tomato"),
            rx.text("Failed to load data", size="3", weight="bold", color="tomato"),
            rx.text(message, size="2", color=white(0.45), text_align="center"),
            spacing="2",
            align="center",
        ),
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=_CARD_RADIUS,
        padding="1.5rem",
        width="100%",
    )


def name_card():
    overview = State.overview

    return rx.cond(
        State.is_loading_company,
        name_card_skeleton(),
        rx.cond(
            State.error_company != "",
            error_card(State.error_company),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.heading(overview.get("symbol", ""), size="9"),
                        rx.button(
                            rx.icon("plus", size=14),
                            size="2",
                            on_click=lambda: CartState.add_item(
                                overview.get("symbol", "")
                            ),
                            style={
                                "background": white(0.05),
                                "border": f"1px solid {white(0.1)}",
                                "border_radius": "8px",
                                "color": white(0.7),
                                "cursor": "pointer",
                                "transition": "all 0.15s ease",
                                "_hover": {
                                    "background": white(0.09),
                                    "border_color": white(0.18),
                                    "color": "white",
                                },
                            },
                        ),
                        justify="center",
                        align="center",
                    ),
                    rx.hstack(
                        rx.badge(
                            f"{overview.get('exchange', '')}",
                            variant="soft",
                            color_scheme="gray",
                            size="1",
                            style={"border_radius": "6px"},
                        ),
                        rx.badge(
                            f"{overview.get('industry', '')}",
                            variant="soft",
                            color_scheme="violet",
                            size="1",
                            style={"border_radius": "6px"},
                        ),
                        spacing="2",
                    ),
                    spacing="3",
                    align="center",
                ),
                background=white(0.025),
                border=CARD_BORDER,
                border_radius=_CARD_RADIUS,
                padding="1.25rem",
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
                rx.box(
                    rx.vstack(
                        rx.text(
                            f"{overview.get('short_name', '')} (Est. {overview.get('established_year', '')})",
                            size="2",
                            color=white(0.8),
                        ),
                        rx.link(
                            website,
                            href=f"https://{website}",
                            is_external=True,
                            size="2",
                            color="var(--accent-9)",
                        ),
                        rx.text(
                            f"Market cap: {overview.get('market_cap', '')} B. VND",
                            size="2",
                            color=white(0.6),
                        ),
                        rx.text(
                            f"Issue Shares: {overview.get('issue_share', '')}",
                            size="2",
                            color=white(0.6),
                        ),
                        rx.text(
                            f"Outstanding Shares: {overview.get('outstanding_share', '')}",
                            size="2",
                            color=white(0.6),
                        ),
                        rx.text(
                            f"{overview.get('no_shareholders', '')} shareholders ({overview.get('foreign_percent', '')}% foreign)",
                            size="2",
                            color=white(0.6),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    background=white(0.025),
                    border=CARD_BORDER,
                    border_radius=_CARD_RADIUS,
                    padding="1.25rem",
                    width="100%",
                ),
                company_profile_dialog(),
                spacing="3",
                width="100%",
            ),
        ),
    )
