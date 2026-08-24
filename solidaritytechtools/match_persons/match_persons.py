"""Deprecated aliases for the old match_persons module.

Everything here moved in 0.4.0: export matching to `solidaritytechtools.export_matching`, and
email lookup to `solidaritytechtools.services.users` (it never touched the json export). The old
names still work and will be removed in a future release.

Names are resolved lazily through a module __getattr__ so the warning fires only when a
deprecated name is actually used, not merely because something imported this module.
"""

# TODO(0.5.0): drop this compatibility shim. Deprecated in 0.4.0, so anyone upgrading has had a
# minor release of warnings to migrate. Removing it means deleting:
#   1. this whole package, solidaritytechtools/match_persons/
#   2. the _DEPRECATED dict, the `__all__ += list(_DEPRECATED)` line, and the __getattr__ at the
#      bottom of solidaritytechtools/__init__.py
#   3. tests/test_deprecated_aliases.py
# The only references to the old names live in those three places; the examples and the package
# internals already use the new ones, so a green test suite after the deletion is a sufficient
# check. Check README.md for stale references too, since it is edited by hand.

from __future__ import annotations

import warnings
from importlib import import_module
from typing import Any, Final

_EXPORT_MATCHING: Final[str] = "solidaritytechtools.export_matching"
_SERVICES_USERS: Final[str] = "solidaritytechtools.services.users"

# old name -> (new module, new name)
_MOVED: Final[dict[str, tuple[str, str]]] = {
    "match_persons": (_EXPORT_MATCHING, "match_export_persons"),
    "find_matches": (_EXPORT_MATCHING, "match_export_file"),
    "find_best_match": (_EXPORT_MATCHING, "best_match_per_person"),
    "find_matches_emails": (_SERVICES_USERS, "match_emails_to_user_ids"),
    "ClientUserMatch": (_EXPORT_MATCHING, "ClientUserMatch"),
    "DEFAULT_CONFIDENCE_THRESHOLD": (_EXPORT_MATCHING, "DEFAULT_CONFIDENCE_THRESHOLD"),
}

__all__ = list(_MOVED)


def __getattr__(name: str) -> Any:
    if name not in _MOVED:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, new_name = _MOVED[name]
    warnings.warn(
        f"solidaritytechtools.match_persons.{name} has moved, it is deprecated and "
        f"will be removed in a future release; use {module}.{new_name} instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(import_module(module), new_name)
