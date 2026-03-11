"""Page modules — auto-discovered from subfolders."""

import importlib
import pkgutil
from pathlib import Path

_pages_dir = Path(__file__).parent

for _mod_info in pkgutil.iter_modules([str(_pages_dir)]):
    if _mod_info.ispkg:
        importlib.import_module(f".{_mod_info.name}", package=__name__)
