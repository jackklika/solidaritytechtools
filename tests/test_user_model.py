from __future__ import annotations

from solidaritytechtools.client.models import User


def test_user_keeps_additional_contact_fields() -> None:
    """other_emails/other_phone_numbers are extra match keys and must survive parsing."""
    user = User.model_validate(
        {
            "id": 1,
            "email": "a@example.com",
            "other_emails": ["b@example.com"],
            "other_phone_numbers": ["4145551234"],
            "tags": ["ActionKit", "Action Network"],
        }
    )
    assert user.other_emails == ["b@example.com"]
    assert user.other_phone_numbers == ["4145551234"]
    assert user.tags == ["ActionKit", "Action Network"]


def test_user_defaults_for_missing_list_fields() -> None:
    user = User(id=1)
    assert user.tags == []
    assert user.other_emails == []
    assert user.other_phone_numbers == []
    assert user.age is None


def test_user_keeps_unknown_fields() -> None:
    """extra='allow' so new api fields aren't silently dropped."""
    user = User.model_validate({"id": 1, "some_new_api_field": "kept"})
    assert user.model_extra is not None
    assert user.model_extra["some_new_api_field"] == "kept"


def test_custom_property_returns_raw_value() -> None:
    user = User(id=1, custom_user_properties={"join-date": "2023-12-27"})
    assert user.custom_property("join-date") == "2023-12-27"
    assert user.custom_property("missing") is None


def test_custom_property_label_from_option_list() -> None:
    """Select/radio properties arrive as a list of {"label", "value"} dicts."""
    user = User(
        id=1,
        custom_user_properties={
            "membership-status": [{"label": "Member in Good Standing", "value": "AfVqfj0n"}]
        },
    )
    assert user.custom_property_label("membership-status") == "Member in Good Standing"


def test_custom_property_label_decodes_unlabeled_code() -> None:
    user = User(id=1, custom_user_properties={"membership-status": [{"value": "AfVqfj0n"}]})
    labels = {"AfVqfj0n": "Member in Good Standing"}
    assert user.custom_property_label("membership-status", value_labels=labels) == (
        "Member in Good Standing"
    )
    # Without a map the opaque code is all we have.
    assert user.custom_property_label("membership-status") == "AfVqfj0n"


def test_custom_property_label_missing_and_empty() -> None:
    assert User(id=1).custom_property_label("membership-status") is None
    empty = User(id=1, custom_user_properties={"membership-status": []})
    assert empty.custom_property_label("membership-status") is None
