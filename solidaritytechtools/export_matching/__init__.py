"""Link an ST json export to a live ST account.

Replaces the old `solidaritytechtools.match_persons` package, which was named after neither of
the two things it joins. The old import paths still work but emit a DeprecationWarning.
"""

from solidaritytechtools.export_matching.matching import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    ClientUserMatch,
    best_match_per_person,
    match_export_file,
    match_export_persons,
)

__all__ = [
    "ClientUserMatch",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "match_export_persons",
    "match_export_file",
    "best_match_per_person",
]
