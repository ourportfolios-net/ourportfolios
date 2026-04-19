"""Navigation bar component."""

import reflex as rx

from ourportfolios.components.search_bar import search_bar
from ourportfolios.state.auth_state import AuthState
from ourportfolios.styles import TEXT_PRIMARY, purple, white


def _nav_link(label: str, href: str) -> rx.Component:
    return rx.link(
        label,
        href=href,
        font_size="0.875rem",
        font_weight="400",
        color=white(0.5),
        text_decoration="none",
        _hover={"color": "white"},
        transition="color 0.2s",
    )


def _locked_nav_link(label: str, href: str) -> rx.Component:
    return rx.hstack(
        rx.text(label, font_size="0.875rem", color=white(0.2)),
        rx.icon("lock", size=10, color=white(0.15)),
        spacing="1",
        align="center",
        on_click=AuthState.redirect_to_login_with_destination(href),
        cursor="pointer",
        title="Sign in to access",
        _hover={"opacity": "0.6"},
        transition="opacity 0.15s",
    )


def _dropdown_item(icon: str, label: str, description: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon, size=17, color=purple(0.75), flex_shrink="0"),
            rx.vstack(
                rx.text(
                    label,
                    font_size="0.875rem",
                    font_weight="500",
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
            border_radius="0.5rem",
            _hover={"background": white(0.05)},
            transition="background 0.12s",
            width="100%",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def _nav_hover_dropdown(label: str, content: rx.Component) -> rx.Component:
    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.hstack(
                rx.text(label, font_size="0.875rem"),
                rx.icon("chevron-down", size=13),
                spacing="1",
                align="center",
                color=white(0.5),
                _hover={"color": "white"},
                transition="color 0.2s",
                cursor="pointer",
            ),
        ),
        rx.hover_card.content(
            content,
            side="bottom",
            align="start",
            side_offset=28,
            background="rgba(13, 13, 15, 0.97)",
            backdrop_filter="blur(1.5rem)",
            border=f"1px solid {white(0.07)}",
            border_radius="0.75rem",
            padding="0.375rem",
            box_shadow="0 1rem 2.5rem rgba(0,0,0,0.55)",
        ),
        open_delay=60,
        close_delay=180,
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
        spacing="0",
        width="17rem",
    )


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


def _menu_item(
    icon: str,
    label: str,
    href: str = "",
    on_click: object = None,
    *,
    danger: bool = False,
) -> rx.Component:
    fg = "rgba(239,68,68,0.75)" if danger else white(0.6)
    hover_bg = "rgba(239,68,68,0.07)" if danger else white(0.05)
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
        border_radius="0.4375rem",
        cursor="pointer",
        transition="background 0.12s",
        _hover={"background": hover_bg},
        width="100%",
    )


def _user_square() -> rx.Component:
    return rx.box(
        rx.text(
            AuthState.user_initial,
            font_size="0.75rem",
            font_weight="600",
            color=white(0.8),
            line_height="1",
            user_select="none",
        ),
        width="2rem",
        height="2rem",
        border_radius="0.5rem",
        background=white(0.06),
        border=f"1px solid {white(0.11)}",
        display="flex",
        align_items="center",
        justify_content="center",
        cursor="pointer",
        flex_shrink="0",
        transition="all 0.15s ease",
        _hover={"background": white(0.1), "border_color": white(0.2)},
    )


def _user_menu() -> rx.Component:
    return rx.dropdown_menu.root(
        rx.dropdown_menu.trigger(_user_square(), as_child=True),
        rx.dropdown_menu.content(
            rx.box(
                rx.vstack(
                    rx.text(
                        rx.cond(
                            AuthState.user_display_name != "",
                            AuthState.user_display_name,
                            AuthState.user_email,
                        ),
                        size="2",
                        weight="medium",
                        color=white(0.85),
                        style={
                            "whiteSpace": "nowrap",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "maxWidth": "12rem",
                        },
                    ),
                    rx.cond(
                        AuthState.user_display_name != "",
                        rx.text(
                            AuthState.user_email,
                            size="1",
                            color=white(0.3),
                            style={
                                "whiteSpace": "nowrap",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "maxWidth": "12rem",
                            },
                        ),
                        rx.fragment(),
                    ),
                    spacing="0",
                    align="start",
                    width="100%",
                ),
                padding="0.55rem 0.6rem 0.6rem",
            ),
            rx.box(
                height="1px",
                background=white(0.07),
                margin_x="0.4rem",
                margin_bottom="0.25rem",
            ),
            _menu_item("settings", "Settings", href="/settings"),
            rx.box(
                height="1px",
                background=white(0.07),
                margin_x="0.4rem",
                margin_y="0.25rem",
            ),
            _menu_item("log-out", "Sign out", on_click=AuthState.logout, danger=True),
            background="rgba(13, 13, 15, 0.97)",
            backdrop_filter="blur(1.5rem)",
            border=f"1px solid {white(0.08)}",
            border_radius="0.75rem",
            padding="0.3rem",
            box_shadow="0 1rem 2.5rem rgba(0,0,0,0.55)",
            min_width="13.5rem",
            side="bottom",
            align="end",
            side_offset=10,
        ),
        modal=False,
    )


def _auth_section() -> rx.Component:
    login_btn = rx.box(
        rx.text("Login", font_size="0.8125rem", font_weight="500", color=white(0.55)),
        on_click=AuthState.redirect_to_login_from_current_page,
        padding="0.35rem 0.85rem",
        border_radius="0.5rem",
        background=white(0.04),
        border=f"1px solid {white(0.09)}",
        cursor="pointer",
        transition="background 0.15s, border-color 0.15s",
        _hover={"background": white(0.08), "border_color": white(0.17)},
    )
    return rx.cond(AuthState.is_authenticated, _user_menu(), login_btn)


def _logo() -> rx.Component:
    return rx.link(
        rx.text(
            "ourportfolios",
            font_size="1.25rem",
            font_weight="600",
            letter_spacing="-0.02em",
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


def navbar() -> rx.Component:
    # ── Shared background/blur styles ────────────────────────────────────────
    bar_style = {
        "position": "fixed",
        "top": "0",
        "width": "100%",
        "z_index": "50",
        "padding_y": "1rem",
        "background": "rgba(10, 10, 10, 0.4)",
        "backdrop_filter": "blur(18px)",
        "border_bottom": f"1px solid {white(0.09)}",
        "box_shadow": "0 10px 40px rgba(0,0,0,0.32)",
    }
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
                padding_x="1rem",
            ),
            style=bar_style,
        ),
    )

    # ── Tablet + Desktop bar: single row with all nav links ───────────────────
    desktop_bar = rx.tablet_and_desktop(
        rx.box(
            rx.hstack(
                rx.hstack(
                    _logo(),
                    _framework_link(),
                    _portfolio_link(),
                    _nav_hover_dropdown("Analyze", _analyze_dropdown()),
                    _nav_hover_dropdown("About", _about_dropdown()),
                    spacing="6",
                    align="center",
                    style={"flexWrap": "wrap"},
                ),
                rx.hstack(
                    search_bar(),
                    _auth_section(),
                    spacing="3",
                    align="center",
                ),
                align="center",
                justify="between",
                width="100%",
                padding_x="2rem",
                style={"flexWrap": "wrap", "gap": "0.75rem"},
            ),
            style=bar_style,
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
