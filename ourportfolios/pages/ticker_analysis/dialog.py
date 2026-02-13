"""Company profile dialog component for displaying detailed company information."""

import reflex as rx
from ...components.cards import glass_card
from ...components.common_dialog import common_dialog
from .state import State


def company_profile_dialog():
    """Dialog component that displays all company profile information in tabs."""
    profile_data = State.profile

    def create_profile_tab_content(content_key: str, tab_value: str):
        return rx.tabs.content(
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
            value=tab_value,
            padding_top="0.8em",
            padding="1em",
        )

    # Dialog content
    dialog_content = rx.tabs.root(
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
        default_value="history",
        width="100%",
        height="100%",
    )

    return rx.fragment(
        # Trigger button
        glass_card(
            rx.hstack(
                rx.icon("info", size=18),
                rx.text("More info", size="2", weight="medium"),
                rx.icon("external-link", size=14),
                spacing="2",
                align="center",
            ),
            padding="0.75em 1em",
            cursor="pointer",
            width="100%",
            on_click=State.set_profile_dialog_open(True),
            style={
                "transition": "all 0.2s ease",
                "_hover": {
                    "transform": "translateY(-1px)",
                    "backgroundColor": rx.color("accent", 2),
                },
            },
        ),
        # Dialog using common_dialog
        common_dialog(
            content=dialog_content,
            is_open=State.profile_dialog_open,
            on_close=State.set_profile_dialog_open(False),
            width="90vw",
            height="85vh",
            max_width="1200px",
            show_close_button=True,
        ),
    )
