from __future__ import annotations

from solidaritytechtools.client import models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.export_matching import (
    ClientUserMatch,
    best_match_per_person,
    match_export_file,
    match_export_persons,
)
from solidaritytechtools.json_export.export import (
    STJsonExport,
    get_persons_from_json_export,
)
from solidaritytechtools.matching import (
    ContactIndex,
    ContactKeys,
    ContactMatch,
    MatchStrategy,
    contact_keys,
    keys_from_mapping,
    keys_from_person,
    keys_from_user,
    match_contacts,
    prefer_member_then_newest,
)
from solidaritytechtools.services.users import (
    UserStore,
    get_all_users,
    match_emails_to_user_ids,
    set_email_permission,
)
from solidaritytechtools.tools.add_traffic_data import add_traffic_data, build_traffic_scorer
from solidaritytechtools.utils.membership import (
    get_join_date,
    get_membership_status,
    get_membership_type,
    is_member_in_good_standing,
)
from solidaritytechtools.utils.normalize import normalize_name, normalize_phone, normalize_zip

__all__ = [
    "STClient",
    "models",
    "STJsonExport",
    "get_persons_from_json_export",
    "match_export_persons",
    "match_export_file",
    "best_match_per_person",
    "match_emails_to_user_ids",
    "ClientUserMatch",
    "ContactIndex",
    "ContactKeys",
    "ContactMatch",
    "MatchStrategy",
    "contact_keys",
    "match_contacts",
    "keys_from_user",
    "keys_from_person",
    "keys_from_mapping",
    "prefer_member_then_newest",
    "get_all_users",
    "UserStore",
    "set_email_permission",
    "add_traffic_data",
    "build_traffic_scorer",
    "get_membership_status",
    "get_membership_type",
    "get_join_date",
    "is_member_in_good_standing",
    "normalize_phone",
    "normalize_name",
    "normalize_zip",
]

# Renamed in 0.4.0. Resolved lazily so `import solidaritytechtools` never warns; the warning
# fires only if one of these names is actually used.
_DEPRECATED: dict[str, str] = {
    "match_persons": "match_export_persons",
    "find_matches": "match_export_file",
    "find_best_match": "best_match_per_person",
    "find_matches_emails": "match_emails_to_user_ids",
}

__all__ += list(_DEPRECATED)


def __getattr__(name: str) -> object:
    if name not in _DEPRECATED:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import warnings

    new_name = _DEPRECATED[name]
    warnings.warn(
        f"solidaritytechtools.{name} is deprecated and will be removed in a future release; "
        f"use solidaritytechtools.{new_name} instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return globals()[new_name]
