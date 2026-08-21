"""Read membership state off an ST User.

Membership isn't a first class field on the api's user object -- it lives in
custom_user_properties under organization-level property keys. Which keys exist, and what the
opaque option codes mean, is per-organization configuration, so it lives here rather than on
the User model. User.custom_property_label handles the wire shape.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Final

from solidaritytechtools.client.models import User

logger = logging.getLogger(__name__)

MEMBERSHIP_STATUS_PROPERTY: Final[str] = "membership-status"
MEMBERSHIP_TYPE_PROPERTY: Final[str] = "membership-type"
JOIN_DATE_PROPERTY: Final[str] = "join-date"
MONTHLY_DUES_STATUS_PROPERTY: Final[str] = "monthly-dues-status"
ENGAGED_NEVER_MEMBER_PROPERTY: Final[str] = "engaged-never-member"

MEMBER_IN_GOOD_STANDING_LABEL: Final[str] = "Member in Good Standing"
MEMBER_IN_GOOD_STANDING_VALUE: Final[str] = "AfVqfj0n"

# Option code -> label for membership-status, used only when a value arrives without its label.
MEMBERSHIP_STATUS_LABELS: Final[dict[str, str]] = {
    MEMBER_IN_GOOD_STANDING_VALUE: MEMBER_IN_GOOD_STANDING_LABEL,
    "pRW0VLhR": "Lapsed",
    "lapsed_member": "Lapsed Member",
    "constitutional_member": "Constitutional Member",
}


def get_property(user: User, key: str) -> Any | None:
    """Return the raw value of a custom user property, or None if unset."""
    return user.custom_property(key)


def get_property_label(
    user: User, key: str, *, value_labels: dict[str, str] | None = None
) -> str | None:
    """
    Return the human readable label of a select/radio custom user property.

    params:
        user: the user to read from
        key: the custom property key, e.g. "membership-status"
        value_labels: optional option code -> label map, used when the api omits the label

    returns: the label, or None if the property is unset or has no readable label
    """
    return user.custom_property_label(key, value_labels=value_labels)


def get_membership_status(user: User) -> str | None:
    """
    Return the user's membership status label, e.g. "Member in Good Standing" or "Lapsed".

    returns: the status label, or None if the user has no membership status set (which is the
        common case -- most people in ST have never been members)
    """
    return get_property_label(
        user, MEMBERSHIP_STATUS_PROPERTY, value_labels=MEMBERSHIP_STATUS_LABELS
    )


def get_membership_type(user: User) -> str | None:
    """Return the dues cadence, e.g. "monthly", "yearly", "one-time" or "income-based"."""
    return get_property_label(user, MEMBERSHIP_TYPE_PROPERTY)


def get_monthly_dues_status(user: User) -> str | None:
    """Return the monthly dues status, e.g. "active", "lapsed" or "past_due"."""
    return get_property_label(user, MONTHLY_DUES_STATUS_PROPERTY)


def get_join_date(user: User) -> date | None:
    """
    Return the date the user became a member, from the "join-date" property.

    This is populated for everyone carrying a membership status. Note that it reflects the
    current membership start, so someone who lapsed and rejoined may show their most recent
    join rather than their first.

    returns: the join date, or None if unset or unparseable
    """
    value = get_property(user, JOIN_DATE_PROPERTY)
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        logger.debug(f"Could not parse {JOIN_DATE_PROPERTY}={value!r} for user {user.id}")
        return None


def is_member_in_good_standing(user: User) -> bool:
    """True if the user's membership-status is "Member in Good Standing"."""
    return get_membership_status(user) == MEMBER_IN_GOOD_STANDING_LABEL


def is_engaged_never_member(user: User) -> bool:
    """True if ST has flagged the user as engaged but never a member."""
    return (get_property_label(user, ENGAGED_NEVER_MEMBER_PROPERTY) or "").lower() == "true"
