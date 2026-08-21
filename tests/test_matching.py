from __future__ import annotations

from dataclasses import dataclass

from solidaritytechtools.client.models import Address, User
from solidaritytechtools.matching import (
    ContactIndex,
    contact_keys,
    keys_from_mapping,
    keys_from_user,
    match_contacts,
    prefer_member_then_newest,
    split_name,
)

MIGS = [{"label": "Member in Good Standing", "value": "AfVqfj0n"}]


@dataclass
class Row:
    """A record type the library knows nothing about."""

    email: str | None = None
    phone: str | None = None
    first: str | None = None
    last: str | None = None
    zip_code: str | None = None


def _row_keys(row: Row):
    return contact_keys(
        emails=row.email,
        phones=row.phone,
        first_name=row.first,
        last_name=row.last,
        postal_code=row.zip_code,
    )


def test_contact_keys_normalizes_everything() -> None:
    keys = contact_keys(
        emails=" Alex@Example.COM ",
        phones="+1 (414) 555-1234",
        first_name="Dana",
        last_name="Quill",
        postal_code="53703-1234",
    )
    assert keys.emails == frozenset({"alex@example.com"})
    assert keys.phones == frozenset({"4145551234"})
    assert keys.name == ("dana", "quill")
    assert keys.zip5 == "53703"


def test_contact_keys_expands_email_subaddress() -> None:
    keys = contact_keys(emails="dana+campaign@example.com")
    assert keys.emails == frozenset({"dana+campaign@example.com", "dana@example.com"})


def test_contact_keys_accepts_many_phones_and_dedupes() -> None:
    keys = contact_keys(phones=["(414) 555-1234", "14145551234", None, "", "555"])
    assert keys.phones == frozenset({"4145551234"})


def test_contact_keys_is_empty() -> None:
    assert contact_keys().is_empty
    assert contact_keys(first_name="Dana").is_empty  # a first name alone identifies nobody
    assert not contact_keys(emails="a@example.com").is_empty


def test_split_name_handles_both_orders() -> None:
    assert split_name("Quill, Dana") == ("Dana", "Quill")
    assert split_name("Dana Quill") == ("Dana", "Quill")
    assert split_name("Dana Marie Quill") == ("Dana", "Quill")
    assert split_name("") == ("", "")


def test_index_matches_arbitrary_record_type() -> None:
    """The index works on any type given an extractor -- no ST model involved."""
    rows = [Row(email="a@example.com"), Row(phone="4145551234")]
    index = ContactIndex(rows, _row_keys)

    by_email = index.match(contact_keys(emails="A@Example.com"))
    assert by_email is not None
    assert by_email.record is rows[0]
    assert by_email.strategy == "email"
    assert by_email.confidence == 1.0

    by_phone = index.match(contact_keys(phones="(414) 555-1234"))
    assert by_phone is not None
    assert by_phone.record is rows[1]
    assert by_phone.strategy == "phone"


def test_stronger_key_wins_over_weaker() -> None:
    """A name match must never override an email match."""
    rows = [
        Row(first="Dana", last="Quill", zip_code="53703"),
        Row(email="dana@example.com", first="Other", last="Person"),
    ]
    index = ContactIndex(rows, _row_keys)
    match = index.match(
        contact_keys(
            emails="dana@example.com", first_name="Dana", last_name="Quill", postal_code="53703"
        )
    )
    assert match is not None
    assert match.strategy == "email"
    assert match.record is rows[1]


def test_name_zip_beats_name_only() -> None:
    rows = [Row(first="Dana", last="Quill", zip_code="53703")]
    index = ContactIndex(rows, _row_keys)
    with_zip = index.match(contact_keys(first_name="Dana", last_name="Quill", postal_code="53703"))
    assert with_zip is not None and with_zip.strategy == "name_zip"
    assert with_zip.confidence == 0.9

    without = index.match(contact_keys(first_name="Dana", last_name="Quill"))
    assert without is not None and without.strategy == "name"
    assert without.confidence == 0.7


def test_ambiguous_name_matches_nobody() -> None:
    """Two people sharing a name must not be matched on name alone."""
    rows = [Row(first="Dana", last="Quill"), Row(first="Dana", last="Quill")]
    index = ContactIndex(rows, _row_keys)
    assert index.match(contact_keys(first_name="Dana", last_name="Quill")) is None


def test_threshold_skips_weak_strategies() -> None:
    rows = [Row(first="Dana", last="Quill")]
    index = ContactIndex(rows, _row_keys)
    assert index.match(contact_keys(first_name="Dana", last_name="Quill")) is not None
    assert index.match(contact_keys(first_name="Dana", last_name="Quill"), threshold=0.9) is None


def test_no_match_returns_none() -> None:
    index = ContactIndex([Row(email="a@example.com")], _row_keys)
    assert index.match(contact_keys(emails="nobody@example.com")) is None
    assert index.match(contact_keys()) is None


def test_candidates_returns_all_sorted() -> None:
    rows = [Row(email="a@example.com"), Row(first="Dana", last="Quill")]
    index = ContactIndex(rows, _row_keys)
    found = index.candidates(
        contact_keys(emails="a@example.com", first_name="Dana", last_name="Quill")
    )
    assert [m.confidence for m in found] == [1.0, 0.7]


def test_keys_from_user_includes_secondary_contacts() -> None:
    user = User(
        id=1,
        email="a@example.com",
        other_emails=["b@example.com"],
        phone_number="14145551234",
        other_phone_numbers=["4145559999"],
        first_name="Dana",
        last_name="Quill",
        address=Address(zip_code="53703-1234"),
    )
    keys = keys_from_user(user)
    assert {"a@example.com", "b@example.com"} <= keys.emails
    assert keys.phones == frozenset({"4145551234", "4145559999"})
    assert keys.zip5 == "53703"


def test_keys_from_mapping_is_header_insensitive() -> None:
    row = {"Email Address": "a@example.com", "Cell_Phone": "(414) 555-1234", "Name": "Quill, Dana"}
    keys = keys_from_mapping(row)
    assert keys.emails == frozenset({"a@example.com"})
    assert keys.phones == frozenset({"4145551234"})
    assert keys.name == ("dana", "quill")


def test_prefer_member_then_newest_tie_breaker() -> None:
    """Duplicate ST records for one human: keep the one showing membership."""
    plain = User(id=1, phone_number="4145551234")
    member = User(
        id=2, phone_number="4145551234", custom_user_properties={"membership-status": MIGS}
    )
    index = ContactIndex([plain, member], keys_from_user, tie_breaker=prefer_member_then_newest)
    match = index.match(contact_keys(phones="4145551234"))
    assert match is not None
    assert match.record.id == 2


def test_match_contacts_maps_left_positions() -> None:
    left = [Row(email="a@example.com"), Row(email="missing@example.com")]
    right = [User(id=7, email="a@example.com")]
    matches = match_contacts(left, right, _row_keys, keys_from_user)
    assert set(matches) == {0}
    assert matches[0].record.id == 7
