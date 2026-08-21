"""Key extractors for common data sources, plus tie-breakers.

An extractor is just `Callable[[YourRecord], ContactKeys]`, so writing one for a new source is
a few lines. These cover the sources this toolset already talks to.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any, Final

from solidaritytechtools.client.models import User
from solidaritytechtools.json_export.models import Person
from solidaritytechtools.matching.keys import ContactKeys, contact_keys

# Header names commonly used for each identifier in csv exports, matched case-insensitively.
DEFAULT_EMAIL_FIELDS: Final[tuple[str, ...]] = ("email", "email address", "emailaddress")
DEFAULT_PHONE_FIELDS: Final[tuple[str, ...]] = (
    "phone",
    "cell phone",
    "cellphone",
    "mobile",
    "home phone",
    "preferred phone",
)
DEFAULT_FIRST_NAME_FIELDS: Final[tuple[str, ...]] = ("first name", "firstname", "first")
DEFAULT_LAST_NAME_FIELDS: Final[tuple[str, ...]] = ("last name", "lastname", "last")
DEFAULT_FULL_NAME_FIELDS: Final[tuple[str, ...]] = ("name", "full name", "fullname")
DEFAULT_POSTAL_FIELDS: Final[tuple[str, ...]] = ("zip", "zip code", "zipcode", "postal code")


def keys_from_user(user: User) -> ContactKeys:
    """Extract keys from an ST api User, including its secondary emails and phones."""
    return contact_keys(
        emails=[user.email, *user.other_emails],
        phones=[user.phone_number, *user.other_phone_numbers],
        first_name=user.first_name,
        last_name=user.last_name,
        postal_code=user.address.zip_code if user.address else None,
    )


def keys_from_person(person: Person) -> ContactKeys:
    """Extract keys from a Person in an ST json export."""
    return contact_keys(
        emails=person.email,
        phones=person.phone_number,
        first_name=person.first_name,
        last_name=person.last_name,
        full_name=person.name,
        postal_code=person.postal_code,
    )


def keys_from_mapping(
    row: Mapping[str, Any],
    *,
    email_fields: Sequence[str] = DEFAULT_EMAIL_FIELDS,
    phone_fields: Sequence[str] = DEFAULT_PHONE_FIELDS,
    first_name_fields: Sequence[str] = DEFAULT_FIRST_NAME_FIELDS,
    last_name_fields: Sequence[str] = DEFAULT_LAST_NAME_FIELDS,
    full_name_fields: Sequence[str] = DEFAULT_FULL_NAME_FIELDS,
    postal_fields: Sequence[str] = DEFAULT_POSTAL_FIELDS,
) -> ContactKeys:
    """
    Extract keys from a dict-like row, e.g. a csv.DictReader row or a dataframe record.

    Field names are matched case-insensitively and ignoring spaces/underscores/hyphens, so
    "Cell Phone", "cell_phone" and "cellphone" all work. Every matching phone and email column
    is collected, since exports routinely spread them across several columns.

    Pair with functools.partial to reuse a configuration:
    ```python
    extractor = partial(keys_from_mapping, phone_fields=("Phone", "Cell Phone"))
    index = ContactIndex(rows, extractor)
    ```
    """
    lookup = {_canonical(key): value for key, value in row.items()}

    def collect(fields: Sequence[str]) -> list[str | None]:
        return [lookup.get(_canonical(field)) for field in fields]

    def first(fields: Sequence[str]) -> str | None:
        for value in collect(fields):
            if value not in (None, ""):
                return str(value)
        return None

    return contact_keys(
        emails=[str(v) for v in collect(email_fields) if v not in (None, "")],
        phones=[str(v) for v in collect(phone_fields) if v not in (None, "")],
        first_name=first(first_name_fields),
        last_name=first(last_name_fields),
        full_name=first(full_name_fields),
        postal_code=first(postal_fields),
    )


def prefer_newest(records: Sequence[User]) -> User:
    """Tie-breaker: the most recently created ST user."""
    return max(records, key=_created_timestamp)


def prefer_member_then_newest(records: Sequence[User]) -> User:
    """
    Tie-breaker: prefer a user carrying a membership status, then the newest.

    ST accumulates duplicate records for the same human. If any of them shows membership then
    the person is a member, so that record is the more informative one to keep.
    """
    from solidaritytechtools.utils.membership import get_membership_status

    return max(
        records,
        key=lambda user: (get_membership_status(user) is not None, _created_timestamp(user)),
    )


def _created_timestamp(user: User) -> float:
    # Compare as epoch seconds: created_at is timezone aware for some users and absent for
    # others, and comparing aware with naive datetimes raises.
    created_at: datetime | None = user.created_at
    return created_at.timestamp() if created_at else 0.0


def _canonical(field: str) -> str:
    return field.strip().lower().replace(" ", "").replace("_", "").replace("-", "")


KeyExtractor = Callable[[Any], ContactKeys]
