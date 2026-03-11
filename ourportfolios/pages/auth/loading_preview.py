"""
Temporary preview route for the session-check loading screen.
Place at: ourportfolios/pages/auth/loading_preview.py
Remove once confirmed working.
"""

import reflex as rx
from .login import session_check_screen


@rx.page(route="/loading")
def loading_preview() -> rx.Component:
    return session_check_screen()
