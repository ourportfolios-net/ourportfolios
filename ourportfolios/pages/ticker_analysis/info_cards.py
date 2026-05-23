"""Information cards with error handling."""

import reflex as rx

from ourportfolios.components.drawer import CartState
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.ui.primitives import (
    badge_text,
    heading,
    hstack,
    icon_button,
    muted_text,
    spacer,
    vstack,
)
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import (
    CARD_BORDER,
    RADIUS_CARD,
)
from ourportfolios.ui.tokens import RADIUS_SM


def _skel(w: str, h: str, radius: str = "0.5rem") -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        style={"border_radius": radius},
    )


def error_card(message: str) -> rx.Component:
    return vstack(
        rx.icon("triangle-alert", size=28, color="tomato"),
        rx.text("Failed to load data", size="3", weight="bold", color="tomato"),
        rx.text(message, size="2", color=white(0.45), text_align="center"),
        spacing="2",
        align="center",
        background=white(0.025),
        border=CARD_BORDER,
        border_radius=RADIUS_CARD,
        padding="1.5rem",
        width="100%",
    )


def name_card() -> rx.Component:
    overview = State.overview

    return rx.cond(
        State.error_company != "",
        error_card(State.error_company),
        rx.box(
            rx.box(
                rx.skeleton(
                    icon_button(
                        "plus",
                        size=14,
                        on_click=lambda: CartState.add_item(
                            overview.get("symbol", ""),
                        ),
                    ),
                    loading=State.is_loading_company,
                    style={"border_radius": RADIUS_SM},
                    border_radius=RADIUS_SM,
                ),
                position="absolute",
                top="1.25rem",
                right="1.25rem",
            ),
            vstack(
                rx.skeleton(
                    heading(
                        rx.cond(
                            State.is_loading_company,
                            "AGG",
                            overview.get("symbol", ""),
                        ),
                        level=1,
                        size="9",
                    ),
                    loading=State.is_loading_company,
                    style={"border_radius": RADIUS_SM},
                    border_radius=RADIUS_SM,
                ),
                hstack(
                    rx.skeleton(
                        badge_text(
                            rx.cond(
                                State.is_loading_company,
                                "HOSE",
                                overview.get("exchange", ""),
                            ),
                            scheme="blue",
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": RADIUS_SM},
                    ),
                    rx.skeleton(
                        badge_text(
                            rx.cond(
                                State.is_loading_company,
                                "Real Estate",
                                overview.get("industry", ""),
                            ),
                            scheme="violet",
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": RADIUS_SM},
                    ),
                    spacing="2",
                ),
                align="start",
                spacing="3",
            ),
            flex_shrink="0",
            position="relative",
            background=white(0.025),
            border=CARD_BORDER,
            border_radius=RADIUS_CARD,
            padding="1.5rem",
            width="100%",
        ),
    )


def general_info_card() -> rx.Component:
    overview = State.overview
    website = rx.cond(
        State.is_loading_company,
        "www.angia.com.vn",
        overview.get("website", ""),
    )

    def _info_row(label: str, value: str | rx.Var[str]) -> rx.Component:
        return hstack(
            muted_text(label),
            spacer(),
            rx.skeleton(
                rx.text(
                    value,
                    size="2",
                    color=white(0.85),
                    weight="medium",
                ),
                loading=State.is_loading_company,
                style={"border_radius": RADIUS_SM},
            ),
            width="100%",
        )

    return rx.cond(
        State.error_company != "",
        error_card(State.error_company),
        rx.box(
            vstack(
                # Header group: name + website tightly spaced
                vstack(
                    rx.skeleton(
                        hstack(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "An Gia Real Estate",
                                    overview.get("short_name", ""),
                                ),
                                size="4",
                                weight="bold",
                                color=white(0.9),
                            ),
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "(Est. 2012)",
                                    f"(Est. {overview.get('established_year', '')})",
                                ),
                                size="2",
                                color=white(0.45),
                            ),
                            spacing="1",
                            align="center",
                            style={"flexWrap": "wrap"},
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": RADIUS_SM},
                    ),
                    rx.skeleton(
                        rx.link(
                            hstack(
                                rx.text(website, size="2", color=rx.color("accent", 9)),
                                rx.icon("link", size=8, color=white(0.4)),
                                align="center",
                                spacing="1",
                            ),
                            href=f"https://{website}",
                            is_external=True,
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": RADIUS_SM},
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                vstack(
                    _info_row(
                        "Market Cap",
                        rx.cond(
                            State.is_loading_company,
                            "2576 B. VND",
                            f"{overview.get('market_cap', '')} B. VND",
                        ),
                    ),
                    _info_row(
                        "Issue Shares",
                        rx.cond(
                            State.is_loading_company,
                            "162.5",
                            f"{overview.get('issue_share', '')}",
                        ),
                    ),
                    _info_row(
                        "Outstanding",
                        rx.cond(
                            State.is_loading_company,
                            "162.5",
                            f"{overview.get('outstanding_share', '')}",
                        ),
                    ),
                    _info_row(
                        "Shareholders",
                        rx.cond(
                            State.is_loading_company,
                            "5921",
                            f"{overview.get('no_shareholders', '')}",
                        ),
                    ),
                    _info_row(
                        "Foreign Owned",
                        rx.cond(
                            State.is_loading_company,
                            "0.8%",
                            f"{overview.get('foreign_percent', '')}%",
                        ),
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="3",
                width="100%",
                align="start",
            ),
            background=white(0.025),
            border=CARD_BORDER,
            border_radius=RADIUS_CARD,
            padding="1.5rem",
            width="100%",
            flex="1",
            min_height="0",
            overflow="hidden",
        ),
    )
