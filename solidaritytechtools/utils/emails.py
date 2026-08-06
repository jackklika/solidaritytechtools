from __future__ import annotations

import re

VALID_EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


def is_valid_email(email_address: str) -> re.Match[str] | None:
    """
    Returns regex match if is valid email, else None if invalid. Email regex from https://emailregex.com/

    This is about 99.99% correct! It will not match certain valid emails, and will think certain
    emails valid to RFC 5322 are invalid. For example "email@-example.com" is invalid but this
    will mark it as valid. But in the end the only thing that matters is if the user receives an
    email :) See https://www.regular-expressions.info/email.html
    """
    return re.match(VALID_EMAIL_REGEX, email_address)


def normalize_email(email_address: str | None) -> str | None:
    """
    Normalize an email for comparison: trimmed and lowercased. Returns None if empty.
    """
    if not email_address:
        return None
    return email_address.strip().lower()


def get_email_local_part(email_address: str) -> str | None:
    """
    Get the part of an email before the @domain, ie 'jack' from 'jack@example.com'.
    Returns None if not a valid address or if it can't find the local part.
    """
    if not is_valid_email(email_address):
        return None
    return email_address.split("@")[0]


def get_email_address_without_subaddress(email_address: str) -> str | None:
    """
    Return the email address without the subaddress.
    For example "jack+abc@example.com" -> "jack@example.com"

    Returns None if invalid.
    """
    email_local_part = get_email_local_part(email_address)
    if not email_local_part:
        return None
    if "+" not in email_local_part:
        return email_address

    domain = email_address.split("@")[1]
    return f"{email_local_part.split('+')[0]}@{domain}"
