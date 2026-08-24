"""Link an ST json export to a live ST account.

This is the export-specific layer: it knows how to load an export file, fetch the account's
users, and pair them up. The matching itself is source agnostic and lives in
solidaritytechtools.matching.

The usual reason to do this is migrating historical data (notes, custom properties) from an old
ST account to a new one, where the two have no shared ids.
"""

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
from solidaritytechtools.services.users import get_all_users

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.8


@dataclass
class ClientUserMatch:
    """An api User an exported Person resolved to, and how much to trust the pairing."""

    user_id: int
    confidence: float


def match_export_persons(
    json_persons: list[json_export_models.Person],
    client_users: list[client_models.User],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[int, list[ClientUserMatch]]:
    """
    Match exported Person objects against api User objects on email, phone and name/zip.

    params:
        json_persons: people loaded from an ST json export
        client_users: users fetched from the target ST account
        threshold: drop matches below this confidence

    returns: mapping of Person.id -> its matches, best confidence first, for people that matched
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


def match_export_file(
    json_export_file: Path | str, api_key: str, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> dict[int, list[ClientUserMatch]]:
    """
    Load a json export, fetch every user from the target account, and match the two.

    params:
        json_export_file: path to the ST json export
        api_key: api key for the account to match against
        threshold: drop matches below this confidence

    returns: mapping of Person.id -> its matches, best confidence first
    """
    logger.info(f"Load people from json export file from {json_export_file}")
    export = STJsonExport.from_path(json_export_file)

    with STClient(api_key=api_key) as client:
        all_users = get_all_users(client)

    return match_export_persons(export.people, all_users, threshold=threshold)


def best_match_per_person(
    json_export_file: Path | str, api_key: str, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> dict[int, ClientUserMatch | None]:
    """
    Reduce match_export_file to a single best match per person.

    Every person in the export gets an entry, so a None value means "no match met the
    threshold" rather than "this person was skipped".

    params:
        json_export_file: path to the ST json export
        api_key: api key for the account to match against
        threshold: drop matches below this confidence

    returns: mapping of Person.id -> its best match, or None
    """
    all_matches = match_export_file(json_export_file, api_key, threshold=threshold)

    export = STJsonExport.from_path(json_export_file)
    results: dict[int, ClientUserMatch | None] = {p.id: None for p in export.people}

    # match_export_file returns matches sorted by confidence, so the first is the best.
    for person_id, matches in all_matches.items():
        if matches:
            results[person_id] = matches[0]

    return results
