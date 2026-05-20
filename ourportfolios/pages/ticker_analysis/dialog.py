"""Company profile dialog component for displaying detailed company information."""

import reflex as rx

from ourportfolios.components.common_dialog import CommonDialogConfig, common_dialog
from ourportfolios.pages.ticker_analysis.state import State
from ourportfolios.ui.primitives import surface_box
from ourportfolios.ui.theme.colors import white
from ourportfolios.ui.theme.surfaces import RADIUS_INPUT
from ourportfolios.ui.tokens import TRANS_DEFAULT

_PROFILE_TEXT_STYLE = {
    "whiteSpace": "pre-wrap",
    "wordWrap": "break-word",
    "textAlign": "justify",
    "lineHeight": "1.6",
}

_DIALOG_TRIGGER_HOVER = {
    "background": white(0.045),
    "border_color": white(0.13),
}


def company_profile_dialog():
    profile_data = State.profile

    def create_profile_tab_content(content_key: str, tab_value: str) -> rx.Component:
        return rx.tabs.content(
            rx.text(
                profile_data.get(content_key, ""),
                size="3",
                weight="regular",
                style=_PROFILE_TEXT_STYLE,
            ),
            value=tab_value,
            padding_top="0.8em",
            padding="1em",
        )

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
        surface_box(
            rx.hstack(
                rx.icon("info", size=15, color=white(0.5)),
                rx.text("More info", size="2", weight="medium", color=white(0.7)),
                rx.icon("external-link", size=12, color=white(0.4)),
                spacing="2",
                align="center",
            ),
            padding="0.6em 0.9em",
            cursor="pointer",
            width="100%",
            on_click=State.set_profile_dialog_open(True),
            background=white(0.025),
            border_radius=RADIUS_INPUT,
            transition=TRANS_DEFAULT,
            _hover=_DIALOG_TRIGGER_HOVER,
        ),
        common_dialog(
            dialog_content,
            CommonDialogConfig(
                is_open=State.profile_dialog_open,
                on_close=State.set_profile_dialog_open(False),
                width="86vw",
                height="85vh",
                max_width="75rem",
                show_close_button=True,
            ),
        ),
    )
