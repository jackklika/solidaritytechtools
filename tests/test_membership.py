from __future__ import annotations

from datetime import date

from solidaritytechtools.client.models import User
from solidaritytechtools.utils.membership import (
    get_join_date,
    get_membership_status,
    get_membership_type,
    get_monthly_dues_status,
    get_property_label,
    is_engaged_never_member,
    is_member_in_good_standing,
)

# The api returns select/radio properties as a list of {"label", "value"} dicts.
MIGS = [{"label": "Member in Good Standing", "value": "AfVqfj0n"}]
LAPSED = [{"label": "Lapsed", "value": "pRW0VLhR"}]


def _user(props: dict[str, object] | None = None, *, user_id: int = 1) -> User:
    """Build a User with custom properties. Keys are hyphenated, so they're passed as a dict."""
    return User(id=user_id, custom_user_properties=props or {})


def test_get_membership_status_uses_label() -> None:
    assert get_membership_status(_user({"membership-status": MIGS})) == "Member in Good Standing"
    assert get_membership_status(_user({"membership-status": LAPSED})) == "Lapsed"


def test_get_membership_status_falls_back_to_option_code() -> None:
    """Codes without a label are decoded through the known option map."""
    unlabeled = [{"value": "constitutional_member"}]
    assert get_membership_status(_user({"membership-status": unlabeled})) == (
        "Constitutional Member"
    )


def test_get_membership_status_unknown_code_passes_through() -> None:
    assert get_membership_status(_user({"membership-status": [{"value": "ZZZ"}]})) == "ZZZ"


def test_get_membership_status_absent() -> None:
    assert get_membership_status(User(id=1)) is None
    assert get_membership_status(_user({"membership-status": []})) is None
    assert get_membership_status(_user({"membership-status": None})) is None


def test_is_member_in_good_standing() -> None:
    assert is_member_in_good_standing(_user({"membership-status": MIGS}))
    assert not is_member_in_good_standing(_user({"membership-status": LAPSED}))
    assert not is_member_in_good_standing(User(id=1))


def test_get_join_date_parses_iso_string() -> None:
    assert get_join_date(_user({"join-date": "2023-12-27"})) == date(2023, 12, 27)


def test_get_join_date_missing_or_invalid() -> None:
    assert get_join_date(User(id=1)) is None
    assert get_join_date(_user({"join-date": ""})) is None
    assert get_join_date(_user({"join-date": "not-a-date"})) is None


def test_get_membership_and_dues_type() -> None:
    user = _user(
        {
            "membership-type": [{"label": "monthly", "value": "45TEdJwW"}],
            "monthly-dues-status": [{"label": "active", "value": "cJ6bJcto"}],
        }
    )
    assert get_membership_type(user) == "monthly"
    assert get_monthly_dues_status(user) == "active"


def test_is_engaged_never_member() -> None:
    flagged = _user({"engaged-never-member": [{"label": "True", "value": "F4phwwnV"}]})
    assert is_engaged_never_member(flagged)
    assert not is_engaged_never_member(User(id=1))


def test_get_property_label_handles_plain_string() -> None:
    """Date and text properties come back as bare strings, not option lists."""
    assert get_property_label(_user({"join-date": "2023-12-27"}), "join-date") == "2023-12-27"
