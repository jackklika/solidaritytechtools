"""Normalizers for comparing people across datasets.

Phone numbers, names and postal codes arrive in inconsistent shapes depending on the source
(the ST api returns 11-digit phones and ZIP+4 postal codes, VAN exports use "(414) 555-1234"
and 5-digit zips). Matching only works if both sides are reduced to the same form first.
"""

from __future__ import annotations

import re
from typing import Final

US_PHONE_DIGITS: Final[int] = 10
_NON_DIGITS: Final[re.Pattern[str]] = re.compile(r"\D")
_NON_LETTERS: Final[re.Pattern[str]] = re.compile(r"[^a-z]")
_ZIP5: Final[re.Pattern[str]] = re.compile(r"(\d{5})")


def normalize_phone(phone: str | None) -> str | None:
    """
    Reduce a phone number to its 10 US digits, dropping a leading country code.

    For example "(414) 555-1234", "+1 414-555-1234" and "14145551234" all become "4145551234".

    returns: the 10 digit number, or None if there aren't exactly 10 digits to work with
    """
    if not phone:
        return None
    digits = _NON_DIGITS.sub("", phone)
    if len(digits) == US_PHONE_DIGITS + 1 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == US_PHONE_DIGITS else None


def normalize_name(name: str | None) -> str:
    """
    Reduce a name to lowercase letters only, so punctuation and spacing stop mattering.

    Source data is hand-entered, so names carry stray punctuation ("Jane :Doe") and
    inconsistent casing. Returns "" when there is nothing left to compare.
    """
    if not name:
        return ""
    return _NON_LETTERS.sub("", name.lower())


def normalize_zip(postal_code: str | None) -> str | None:
    """
    Reduce a postal code to its 5 digit prefix, so ZIP+4 compares equal to ZIP5.

    The ST api and json export return ZIP+4 ("53703-1234") while VAN data is 5 digit
    ("53703"), so comparing them raw never matches.

    returns: the 5 digit zip, or None if there isn't one
    """
    if not postal_code:
        return None
    match = _ZIP5.search(postal_code.strip())
    return match.group(1) if match else None
