"""Place at: ourportfolios/components/auth_guard.py.

Provides page_guard() — wrap every protected page's content with this.
The blank dark screen is rendered on first paint (auth_checked=False);
content is revealed only after require_auth() validates the session.
"""

import reflex as rx

from ourportfolios.state.auth_state import AuthState


def page_guard(content: rx.Component, bg: str = "#090909") -> rx.Component:
    """Wrap protected page content in an auth gate.

    Usage in any protected page's index():
        return page_guard(_page_body())

    The blank screen shares the same background as the app so there is no
    colour flash before the redirect to /auth fires.
    """
    return rx.cond(
        AuthState.auth_checked,
        content,
        rx.box(background=bg, min_height="100vh", width="100%"),
    )
