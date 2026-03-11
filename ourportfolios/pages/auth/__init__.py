from .client import AUTH_AVAILABLE

if AUTH_AVAILABLE:
    from .login import login
    from .callback import callback

    __all__ = ["login", "callback"]
else:
    __all__ = []
