import logging
import re
from pathlib import Path
from typing import Final

from pydantic.dataclasses import dataclass

import solidaritytechtools.client.models as client_models
import solidaritytechtools.json_export.models as json_export_models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.json_export.export import STJsonExport

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.8


@dataclass
class ClientUserMatch:
    user_id: int
    confidence: float


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    # Strip all non-digits
    digits = re.sub(r"\D", "", phone)
    # Handle US country code if present (e.g., 14145551234 -> 4145551234)
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:]
    return digits


def _normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    return email.strip().lower()


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""
    return name.strip().lower()


def match_persons(
    json_persons: list[json_export_models.Person],
    client_users: list[client_models.User],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[int, list[ClientUserMatch]]:
    """
    Attempts to match exported Person objects with API User objects based on
    email, phone number, and name/address similarity.

    Returns a mapping of Person.id -> list of ClientUserMatch objects.
    """
    # 1. Build indices for client_users to avoid O(N*M)
    email_map: dict[str, list[client_models.User]] = {}
    phone_map: dict[str, list[client_models.User]] = {}
    name_map: dict[tuple[str, str], list[client_models.User]] = {}

    for user in client_users:
        # Index by Email
        if email := _normalize_email(user.email):
            email_map.setdefault(email, []).append(user)

        # Index by Phone
        if phone := _normalize_phone(user.phone_number):
            phone_map.setdefault(phone, []).append(user)

        # Index by First + Last Name
        fname = _normalize_name(user.first_name)
        lname = _normalize_name(user.last_name)
        if fname and lname:
            name_map.setdefault((fname, lname), []).append(user)

    results: dict[int, list[ClientUserMatch]] = {}

    # 2. Iterate through persons and find candidates
    for person in json_persons:
        # Tracks user_id -> highest confidence found for this person
        candidates: dict[int, float] = {}

        p_email = _normalize_email(person.email)
        p_phone = _normalize_phone(person.phone_number)
        p_fname = _normalize_name(person.first_name)
        p_lname = _normalize_name(person.last_name)
        p_zip = (person.postal_code or "").strip()

        # Check Email Matches (Confidence 1.0)
        if p_email and p_email in email_map:
            for u in email_map[p_email]:
                candidates[u.id] = max(candidates.get(u.id, 0), 1.0)

        # Check Phone Matches (Confidence 1.0)
        if p_phone and p_phone in phone_map:
            for u in phone_map[p_phone]:
                candidates[u.id] = max(candidates.get(u.id, 0), 1.0)

        # Check Name Matches
        if p_fname and p_lname and (p_fname, p_lname) in name_map:
            for u in name_map[(p_fname, p_lname)]:
                # If Name matches, check Zip Code for higher confidence
                u_zip = ""
                if u.address and hasattr(u.address, "zip_code"):
                    u_zip = (u.address.zip_code or "").strip()
                elif isinstance(u.address, dict):
                    u_zip = str(u.address.get("zip_code", "")).strip()

                if p_zip and u_zip and p_zip == u_zip:
                    conf = 0.9  # Name + Zip
                else:
                    conf = 0.7  # Name only

                candidates[u.id] = max(candidates.get(u.id, 0), conf)

        # 3. Filter by threshold and sort
        person_matches = [
            ClientUserMatch(user_id=uid, confidence=conf)
            for uid, conf in candidates.items()
            if conf >= threshold
        ]

        if person_matches:
            # Sort matches by confidence descending
            person_matches.sort(key=lambda x: x.confidence, reverse=True)
            results[person.id] = person_matches

    return results


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

    all_users: list[client_models.User] = []
    with STClient(api_key=api_key) as client:
        limit = 100
        offset = 0
        while True:
            logger.info(f"Fetching users from api limit={limit} offset={offset}")
            response = client.get_users(limit=limit, offset=offset)
            if not response.data:
                break

            all_users.extend(response.data)

            # Check if we've reached the end based on total_count
            if response.meta and response.meta.total_count is not None:
                if len(all_users) >= response.meta.total_count:
                    break

            # Safety break if we got less than requested
            if len(response.data) < limit:
                break

            offset += limit

    # 3. Perform matching
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
