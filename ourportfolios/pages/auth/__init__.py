from .client import AUTH_AVAILABLE

if AUTH_AVAILABLE:
    from .login import login
    from .callback import callback
    from .reset_callback import reset_callback
    from .reset_password import reset_password

    __all__ = ["login", "callback", "reset_callback", "reset_password"]
else:
    __all__ = []
