from __future__ import annotations

from solidaritytechtools.utils.normalize import normalize_name, normalize_phone, normalize_zip


def test_normalize_phone_strips_formatting() -> None:
    assert normalize_phone("(414) 555-1234") == "4145551234"
    assert normalize_phone("414.555.1234") == "4145551234"
    assert normalize_phone("4145551234") == "4145551234"


def test_normalize_phone_drops_us_country_code() -> None:
    assert normalize_phone("14145551234") == "4145551234"
    assert normalize_phone("+1 (414) 555-1234") == "4145551234"


def test_normalize_phone_rejects_wrong_length() -> None:
    assert normalize_phone("555-1234") is None
    assert normalize_phone("24145551234") is None
    assert normalize_phone("") is None
    assert normalize_phone(None) is None


def test_normalize_name_keeps_letters_only() -> None:
    assert normalize_name("John Smith") == "johnsmith"
    # Hand-entered source data carries stray punctuation.
    assert normalize_name("Jane :Doe") == "janedoe"
    assert normalize_name("O'Public-Doe") == "opublicdoe"
    assert normalize_name("  doe  ") == "doe"


def test_normalize_name_empty() -> None:
    assert normalize_name(None) == ""
    assert normalize_name("") == ""
    assert normalize_name("123") == ""


def test_normalize_zip_reduces_zip_plus_four() -> None:
    assert normalize_zip("53703-1234") == "53703"
    assert normalize_zip("53703") == "53703"
    assert normalize_zip(" 53703 ") == "53703"


def test_normalize_zip_missing() -> None:
    assert normalize_zip(None) is None
    assert normalize_zip("") is None
    assert normalize_zip("WI") is None
