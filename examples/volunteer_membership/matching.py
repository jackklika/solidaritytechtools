"""Match volunteers to Solidarity Tech users.

All the matching logic lives in solidaritytechtools.matching, which is source agnostic. This
only says how to pull identifiers out of a Volunteer and which tie-breaker to use.
"""

from __future__ import annotations

import logging
from typing import Final

from roster import Volunteer

from solidaritytechtools.client.models import User
from solidaritytechtools.matching import (
    ContactKeys,
    ContactMatch,
    contact_keys,
    keys_from_user,
    match_contacts,
    prefer_member_then_newest,
)

logger = logging.getLogger(__name__)

# Headline figures only trust matches at or above this confidence, which excludes name-only
# matches (0.7) while keeping email, phone and name+zip.
DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.9

VolunteerMatch = ContactMatch[User]


def keys_from_volunteer(volunteer: Volunteer) -> ContactKeys:
    """Pull the identifiers a volunteer can be matched on."""
    return contact_keys(
        emails=volunteer.email,
        phones=sorted(volunteer.phones),
        first_name=volunteer.first_name,
        last_name=volunteer.last_name,
        postal_code=volunteer.zip5,
    )


def match_roster(roster: list[Volunteer], users: list[User]) -> dict[int, VolunteerMatch]:
    """
    Match every volunteer in the roster to an ST user.

    params:
        roster: the deduplicated volunteer roster
        users: every ST user to match against

    returns: mapping of the volunteer's index in the roster -> its match, for those that matched
    """
    return match_contacts(
        roster,
        users,
        keys_from_volunteer,
        keys_from_user,
        tie_breaker=prefer_member_then_newest,
    )
