from __future__ import annotations

import warnings

import pytest

import solidaritytechtools
from solidaritytechtools.export_matching import (
    ClientUserMatch,
    best_match_per_person,
    match_export_file,
    match_export_persons,
)
from solidaritytechtools.services.users import match_emails_to_user_ids

# old top-level name -> the object it should now resolve to
RENAMED = [
    ("match_persons", match_export_persons),
    ("find_matches", match_export_file),
    ("find_best_match", best_match_per_person),
    ("find_matches_emails", match_emails_to_user_ids),
]


def test_plain_import_does_not_warn() -> None:
    """Nobody should see a DeprecationWarning just for importing the package."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        importlib = __import__("importlib")
        importlib.reload(solidaritytechtools)


@pytest.mark.parametrize(("old_name", "new_obj"), RENAMED)
def test_old_top_level_name_still_resolves(old_name: str, new_obj: object) -> None:
    with pytest.deprecated_call():
        assert getattr(solidaritytechtools, old_name) is new_obj


@pytest.mark.parametrize(("old_name", "new_obj"), RENAMED)
def test_old_module_path_still_resolves(old_name: str, new_obj: object) -> None:
    from solidaritytechtools.match_persons import match_persons as shim

    with pytest.deprecated_call():
        assert getattr(shim, old_name) is new_obj


def test_client_user_match_is_reexported() -> None:
    from solidaritytechtools.match_persons import match_persons as shim

    with pytest.deprecated_call():
        assert shim.ClientUserMatch is ClientUserMatch


def test_unknown_name_still_raises_attribute_error() -> None:
    from solidaritytechtools.match_persons import match_persons as shim

    with pytest.raises(AttributeError):
        _ = shim.definitely_not_a_real_name
    with pytest.raises(AttributeError):
        _ = solidaritytechtools.definitely_not_a_real_name


def test_old_names_are_in_all_so_star_import_keeps_working() -> None:
    for old_name, _ in RENAMED:
        assert old_name in solidaritytechtools.__all__
