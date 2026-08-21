"""Utilities for matching ST json exports to another ST instance"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from pydantic.dataclasses import dataclass

import solidaritytechtools.client.models as client_models
import solidaritytechtools.json_export.models as json_export_models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.json_export.export import STJsonExport
from solidaritytechtools.matching import ContactIndex, keys_from_person, keys_from_user
from solidaritytechtools.services.users import UserStore, get_all_users

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.8


@dataclass
class ClientUserMatch:
    user_id: int
    confidence: float


def match_persons(
    json_persons: list[json_export_models.Person],
    client_users: list[client_models.User],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[int, list[ClientUserMatch]]:
    """
    Attempts to match exported Person objects with API User objects based on
    email, phone number, and name/address similarity.

    Matching itself lives in solidaritytechtools.matching, which is source agnostic; this just
    wires the two ST record types into it.

    Returns a mapping of Person.id -> list of ClientUserMatch objects.
    """
    index = ContactIndex(client_users, keys_from_user)

    results: dict[int, list[ClientUserMatch]] = {}
    for person in json_persons:
        candidates = [
            ClientUserMatch(user_id=match.record.id, confidence=match.confidence)
            for match in index.candidates(keys_from_person(person))
            if match.confidence >= threshold
        ]
        if candidates:
            results[person.id] = candidates

    return results


def find_matches_emails(
    emails: list[str], *, api_key: str, strip_subaddress: bool = True, refresh: bool = False
) -> dict[str, int]:
    """
    Given a list of emails, find matching accounts in ST.

    Loads all users once into a cached UserStore and matches locally, rather than making one
    API call per email.

    params:
        emails: list of email addresses
        api_key: api key to auth with ST with
        strip_subaddress: If True, also match without email subaddresses,
            ie map jack+123@example.com to jack@example.com, on either side (input or ST account)
        refresh: if True, ignore the on-disk user cache and re-fetch from the API

    returns: mapping of input email -> integer Solidarity Tech ID, only for emails that matched
    """
    store = UserStore.from_api(api_key, refresh=refresh)
    return store.match_emails(emails, strip_subaddress=strip_subaddress)


def find_matches(
    json_export_file: Path | str, api_key: str, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> dict[int, list[ClientUserMatch]]:
    """
    Convenience function that loads a JSON export, fetches all users from the API,
    and returns a mapping of matches.
    """
    logger.info(f"Load people from json export file from {json_export_file}")
    export = STJsonExport.from_path(json_export_file)
    json_persons = export.people

    with STClient(api_key=api_key) as client:
        all_users = get_all_users(client)

    return match_persons(json_persons, all_users, threshold=threshold)


def find_best_match(
    json_export_file: Path | str, api_key: str, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> dict[int, ClientUserMatch | None]:
    """
    Returns a dictionary mapping Person ID to the single best ClientUserMatch found,
    or None if no match meets the threshold.
    """
    all_matches = find_matches(json_export_file, api_key, threshold=threshold)

    # Load exported persons to ensure we return an entry for everyone in the export
    export = STJsonExport.from_path(json_export_file)
    results: dict[int, ClientUserMatch | None] = {p.id: None for p in export.people}

    # Since find_matches returns matches sorted by confidence, just take the first one
    for person_id, matches in all_matches.items():
        if matches:
            results[person_id] = matches[0]

    return results
