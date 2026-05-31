"""Navigation bar component."""

import reflex as rx

from ourportfolios.components.search_bar import search_bar
from ourportfolios.state.auth_state import AuthState
from ourportfolios.ui.primitives import (
    divider,
    dropdown_panel,
    locked_link,
    nav_link,
    truncated_text,
    user_avatar,
)
from ourportfolios.ui.theme.colors import TEXT_PRIMARY, purple, white
from ourportfolios.ui.tokens import (
    BLUR_DEFAULT,
    FONT_BASE,
    FONT_XL,
    LETTER_SNUG,
    RADIUS_MD,
    RADIUS_SM,
    SHADOW_LG,
    SPACE_LG,
    SPACE_SM,
    SPACE_XL,
    TRANS_DEFAULT,
    WEIGHT_MEDIUM,
    WEIGHT_SEMIBOLD,
)


def _nav_link(label: str, href: str) -> rx.Component:
    """Navigation link with hover transition."""
    return nav_link(label, href=href)


def _locked_nav_link(label: str, href: str) -> rx.Component:
    """Locked nav link that redirects to login."""
    return locked_link(
        label,
        _href=href,
        on_click=AuthState.redirect_to_login_with_destination(href),
    )


def _dropdown_item(icon: str, label: str, description: str, href: str) -> rx.Component:
    """Dropdown menu item with icon and description."""
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon, size=17, color=purple(0.75), flex_shrink="0"),
            rx.vstack(
                rx.text(
                    label,
                    font_size=FONT_BASE,
                    font_weight=WEIGHT_MEDIUM,
                    color=TEXT_PRIMARY,
                ),
                rx.text(
                    description,
                    font_size="0.72rem",
                    color=white(0.35),
                    line_height="1.4",
                ),
                spacing="1",
            ),
            spacing="3",
            align="start",
            padding="0.55rem 0.65rem",
            border_radius=RADIUS_SM,
            _hover={"background": white(0.05)},
            transition=TRANS_DEFAULT,
            width="100%",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def _nav_hover_dropdown(label: str, content: rx.Component) -> rx.Component:
    """Hover-triggered dropdown with glass panel."""
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.text(label, font_size=FONT_BASE),
                rx.icon("chevron-down", size=13),
                spacing="1",
                align="center",
                color=white(0.5),
                _hover={"color": "white"},
                transition=TRANS_DEFAULT,
                cursor="pointer",
            ),
        ),
        rx.hover_card.content(
            dropdown_panel(content),
            side="bottom",
            align="start",
            side_offset=28,
            open_delay=0,
            close_delay=0,
            background="transparent",
            border="none",
            box_shadow="none",
            padding="0",
        ),
    )


def _analyze_dropdown() -> rx.Component:
    return rx.vstack(
        _dropdown_item(
            "line-chart",
            "Market",
            "Market overview and trends",
            "/analyze",
        ),
        _dropdown_item(
            "factory",
            "Industries",
            "Explore sectors and industries",
            "/select",
        ),
        _dropdown_item(
            "git-compare-arrows",
            "Individual Tickers",
            "Side-by-side comparison",
            "/tickers",
        ),
        spacing="0",
        width="17rem",
    )


def _about_dropdown() -> rx.Component:
    return rx.vstack(
        _dropdown_item(
            "users",
            "ourteam",
            "Meet the people behind ourportfolios",
            "/about/team",
        ),
        _dropdown_item(
            "briefcase",
            "ourportfolios",
            "Learn more about the project",
            "/about",
        ),
        _dropdown_item(
            "mail",
            "Contact",
            "Get in touch with us",
            "/contacts",
        ),
        spacing="0",
        width="17rem",
    )


def _graph_link() -> rx.Component:
    return _nav_link("Graph", "/graph")


def _framework_link() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        _nav_link("Frameworks", "/framework"),
        _locked_nav_link("Frameworks", "/framework"),
    )


def _portfolio_link() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        _nav_link("Portfolio", "/portfolio-management"),
        _locked_nav_link("Portfolio", "/portfolio-management"),
    )


# ── User menu ─────────────────────────────────────────────────────────────────


_menu_item_danger_fg = "rgba(239,68,68,0.75)"
_menu_item_danger_hover = "rgba(239,68,68,0.07)"


def _menu_item(
    icon: str,
    label: str,
    href: str = "",
    on_click: object = None,
    *,
    danger: bool = False,
) -> rx.Component:
    fg = _menu_item_danger_fg if danger else white(0.6)
    hover_bg = _menu_item_danger_hover if danger else white(0.05)
    click_handler = rx.redirect(href) if href else on_click
    return rx.box(
        rx.hstack(
            rx.icon(icon, size=13, color=fg, flex_shrink="0"),
            rx.text(label, size="2", weight="medium", color=fg),
            spacing="2",
            align="center",
        ),
        on_click=click_handler,
        padding="0.45rem 0.6rem",
        border_radius=RADIUS_SM,
        cursor="pointer",
        transition=TRANS_DEFAULT,
        _hover={"background": hover_bg},
        width="100%",
    )


def _user_square() -> rx.Component:
    """User avatar with initial letter. Uses user_avatar primitive."""
    return user_avatar(initial=AuthState.user_initial)


def _user_menu() -> rx.Component:
    return rx.dropdown_menu.root(
        rx.dropdown_menu.trigger(_user_square(), as_child=True),
        rx.dropdown_menu.content(
            rx.box(
                rx.vstack(
                    truncated_text(
                        rx.cond(
                            AuthState.user_display_name != "",
                            AuthState.user_display_name,
                            AuthState.user_email,
                        ),
                        max_width="12rem",
                        size="2",
                        weight="medium",
                        color=white(0.85),
                    ),
                    rx.cond(
                        AuthState.user_display_name != "",
                        truncated_text(
                            AuthState.user_email,
                            max_width="12rem",
                            size="1",
                            color=white(0.3),
                        ),
                        rx.fragment(),
                    ),
                    spacing="0",
                    align="start",
                    width="100%",
                ),
                padding="0.55rem 0.6rem 0.6rem",
            ),
            divider(),
            _menu_item("settings", "Settings", href="/settings"),
            divider(),
            _menu_item("log-out", "Sign out", on_click=AuthState.logout, danger=True),
            background="rgba(13, 13, 15, 0.97)",
            border=f"1px solid {white(0.08)}",
            border_radius=RADIUS_MD,
            padding="0.3rem",
            box_shadow=SHADOW_LG,
            min_width="13.5rem",
            side="bottom",
            align="end",
            side_offset=10,
        ),
        modal=False,
    )


def _auth_section() -> rx.Component:
    login_button = rx.box(
        rx.text("Login", size="2", weight="medium", color=white(0.55)),
        on_click=AuthState.redirect_to_login_from_current_page,
        padding="0.35rem 0.85rem",
        border_radius=RADIUS_SM,
        background=white(0.04),
        border=f"1px solid {white(0.09)}",
        cursor="pointer",
        transition=TRANS_DEFAULT,
        _hover={"background": white(0.08), "border_color": white(0.17)},
    )
    return rx.cond(AuthState.is_authenticated, _user_menu(), login_button)


def _logo() -> rx.Component:
    return rx.link(
        rx.text(
            "ourportfolios",
            font_size=FONT_XL,
            font_weight=WEIGHT_SEMIBOLD,
            letter_spacing=LETTER_SNUG,
            user_select="none",
            flex_shrink="0",
        ),
        href="/home",
        text_decoration="none",
        color="inherit",
        _hover={
            "cursor": "pointer",
            "text_decoration": "none",
            "color": "inherit",
        },
    )


# ── Navbar ────────────────────────────────────────────────────────────────────

_NAVBAR_STYLE = {
    "position": "fixed",
    "top": "0",
    "width": "100%",
    "z_index": "50",
    "padding_y": "1rem",
    "background": "rgba(10, 10, 10, 0.4)",
    "backdrop_filter": f"blur({BLUR_DEFAULT})",
    "border_bottom": f"1px solid {white(0.09)}",
    "box_shadow": SHADOW_LG,
}


def navbar() -> rx.Component:
    # ── Mobile bar: logo + auth on row 1, full-width search on row 2 ─────────
    mobile_bar = rx.mobile_only(
        rx.box(
            rx.vstack(
                rx.hstack(
                    _logo(),
                    rx.spacer(),
                    _auth_section(),
                    align="center",
                    width="100%",
                ),
                rx.box(
                    search_bar(),
                    width="100%",
                ),
                spacing="2",
                width="100%",
                padding_x=SPACE_LG,
            ),
            style=_NAVBAR_STYLE,
        ),
    )

    # ── Tablet + Desktop bar: single row with all nav links ───────────────────
    desktop_bar = rx.tablet_and_desktop(
        rx.box(
            rx.hstack(
                rx.hstack(
                    _logo(),
                    _graph_link(),
                    _framework_link(),
                    _portfolio_link(),
                    _nav_hover_dropdown("Analyze", _analyze_dropdown()),
                    _nav_hover_dropdown("About", _about_dropdown()),
                    spacing="6",
                    align="center",
                    flex_wrap="wrap",
                ),
                rx.hstack(
                    search_bar(),
                    _auth_section(),
                    spacing="3",
                    align="center",
                    flex_wrap="wrap",
                    gap=SPACE_SM,
                ),
                align="center",
                justify="between",
                width="100%",
                padding_x=SPACE_XL,
            ),
            style=_NAVBAR_STYLE,
        ),
    )

    # Spacer height matches bar height:
    # mobile  → ~7rem (two rows: logo/auth + search + padding)
    # tablet+ → ~4rem (single row + padding)
    spacer = rx.box(
        height=rx.breakpoints(initial="7rem", sm="4rem"),
        width="100%",
    )

    return rx.fragment(mobile_bar, desktop_bar, spacer)
