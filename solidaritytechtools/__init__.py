from __future__ import annotations

from solidaritytechtools.client import models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.json_export.export import (
    STJsonExport,
    get_persons_from_json_export,
)
from solidaritytechtools.match_persons.match_persons import (
    find_best_match,
    find_matches,
    find_matches_emails,
    match_persons,
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
from solidaritytechtools.services.users import UserStore, get_all_users, set_email_permission
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
    "match_persons",
    "find_matches",
    "find_best_match",
    "find_matches_emails",
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
