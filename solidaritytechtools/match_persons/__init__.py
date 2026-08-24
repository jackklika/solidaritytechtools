"""Deprecated. Use `solidaritytechtools.export_matching` instead.

Kept so `from solidaritytechtools.match_persons import find_best_match` keeps working; the
names resolve lazily so importing the package alone does not warn.
"""

from __future__ import annotations

from typing import Any

from solidaritytechtools.match_persons.match_persons import _MOVED


def __getattr__(name: str) -> Any:
    if name not in _MOVED:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from solidaritytechtools.match_persons import match_persons as _shim

    return getattr(_shim, name)
