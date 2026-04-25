"""Information cards with error handling."""

import reflex as rx

from ourportfolios.components.drawer import CartState
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.styles import CARD_BORDER, white

_CARD_RADIUS = "0.625rem"


def _skel(w: str, h: str, radius: str = "0.5rem") -> rx.Component:
    return rx.skeleton(
        rx.box(width=w, height=h),
        loading=True,
        style={"border_radius": radius},
    )


def error_card(message: str) -> rx.Component:
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


def name_card() -> rx.Component:
    overview = State.overview

    return rx.cond(
        State.error_company != "",
        error_card(State.error_company),
        rx.box(
            rx.box(
                rx.skeleton(
                    rx.button(
                        rx.icon("plus", size=14),
                        size="2",
                        on_click=lambda: CartState.add_item(
                            overview.get("symbol", ""),
                        ),
                        style={
                            "background": white(0.05),
                            "border": f"1px solid {white(0.1)}",
                            "border_radius": "0.5rem",
                            "color": white(0.7),
                            "cursor": "pointer",
                            "padding": "0.4rem",
                            "transition": "all 0.15s ease",
                            "_hover": {
                                "background": white(0.09),
                                "border_color": white(0.18),
                                "color": "white",
                            },
                        },
                    ),
                    loading=State.is_loading_company,
                    style={"border_radius": "0.375rem"},
                    border_radius="0.5rem",
                ),
                position="absolute",
                top="1.25rem",
                right="1.25rem",
            ),
            rx.vstack(
                rx.skeleton(
                    rx.heading(
                        rx.cond(
                            State.is_loading_company,
                            "AGG",
                            overview.get("symbol", ""),
                        ),
                        size="9",
                        weight="bold",
                        line_height="1",
                    ),
                    loading=State.is_loading_company,
                    style={"border_radius": "0.375rem"},
                    border_radius="0.5rem",
                ),
                rx.hstack(
                    rx.skeleton(
                        rx.badge(
                            rx.cond(
                                State.is_loading_company,
                                "HOSE",
                                overview.get("exchange", ""),
                            ),
                            variant="soft",
                            color_scheme="gray",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": "0.375rem"},
                    ),
                    rx.skeleton(
                        rx.badge(
                            rx.cond(
                                State.is_loading_company,
                                "Real Estate",
                                overview.get("industry", ""),
                            ),
                            variant="soft",
                            color_scheme="violet",
                            size="1",
                            style={"border_radius": "0.375rem"},
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": "0.375rem"},
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
            border_radius=_CARD_RADIUS,
            padding="1.25rem",
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

    return rx.cond(
        State.error_company != "",
        error_card(State.error_company),
        rx.box(
            rx.vstack(
                # Header group: name + website tightly spaced
                rx.vstack(
                    rx.skeleton(
                        rx.hstack(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "An Gia Real Estate",
                                    overview.get("short_name", ""),
                                ),
                                size="2",
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
                        style={"border_radius": "0.375rem"},
                    ),
                    rx.skeleton(
                        rx.link(
                            rx.hstack(
                                rx.text(website, size="2", color=rx.color("accent", 9)),
                                rx.icon("link", size=8, color=white(0.4)),
                                align="center",
                                spacing="1",
                            ),
                            href=f"https://{website}",
                            is_external=True,
                        ),
                        loading=State.is_loading_company,
                        style={"border_radius": "0.375rem"},
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Market Cap", size="2", color=white(0.5)),
                        rx.spacer(),
                        rx.skeleton(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "2576 B. VND",
                                    f"{overview.get('market_cap', '')} B. VND",
                                ),
                                size="2",
                                color=white(0.85),
                                weight="medium",
                            ),
                            loading=State.is_loading_company,
                            style={"border_radius": "0.375rem"},
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Issue Shares", size="2", color=white(0.5)),
                        rx.spacer(),
                        rx.skeleton(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "162.5",
                                    f"{overview.get('issue_share', '')}",
                                ),
                                size="2",
                                color=white(0.85),
                                weight="medium",
                            ),
                            loading=State.is_loading_company,
                            style={"border_radius": "0.375rem"},
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Outstanding", size="2", color=white(0.5)),
                        rx.spacer(),
                        rx.skeleton(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "162.5",
                                    f"{overview.get('outstanding_share', '')}",
                                ),
                                size="2",
                                color=white(0.85),
                                weight="medium",
                            ),
                            loading=State.is_loading_company,
                            style={"border_radius": "0.375rem"},
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Shareholders", size="2", color=white(0.5)),
                        rx.spacer(),
                        rx.skeleton(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "5921",
                                    f"{overview.get('no_shareholders', '')}",
                                ),
                                size="2",
                                color=white(0.85),
                                weight="medium",
                            ),
                            loading=State.is_loading_company,
                            style={"border_radius": "0.375rem"},
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Foreign Owned", size="2", color=white(0.5)),
                        rx.spacer(),
                        rx.skeleton(
                            rx.text(
                                rx.cond(
                                    State.is_loading_company,
                                    "0.8%",
                                    f"{overview.get('foreign_percent', '')}%",
                                ),
                                size="2",
                                color=white(0.85),
                                weight="medium",
                            ),
                            loading=State.is_loading_company,
                            style={"border_radius": "0.375rem"},
                        ),
                        width="100%",
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
            border_radius=_CARD_RADIUS,
            padding="1.25rem",
            width="100%",
            flex="1",
            min_height="0",
            overflow="hidden",
        ),
    )
