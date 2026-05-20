from ourportfolios.auth_config import AUTH_AVAILABLE

if AUTH_AVAILABLE:
    from ourportfolios.pages.auth.callback import callback
    from ourportfolios.pages.auth.login import login
    from ourportfolios.pages.auth.reset_callback import reset_callback
    from ourportfolios.pages.auth.reset_password import reset_password

    __all__ = ["callback", "login", "reset_callback", "reset_password"]
else:
    __all__ = []
