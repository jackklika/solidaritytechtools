"""Normalized identifiers for one contact, from any data source.

Matching people across datasets only works if both sides are reduced to the same form first,
so every identifier here is normalized on construction. Build these with contact_keys(), which
takes whatever raw values a source happens to have.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from solidaritytechtools.utils.emails import get_email_address_without_subaddress, normalize_email
from solidaritytechtools.utils.normalize import normalize_name, normalize_phone, normalize_zip


@dataclass(frozen=True)
class ContactKeys:
    """
    The normalized identifiers for one person.

    Every field is already normalized: emails lowercased, phones reduced to 10 digits, names
    to lowercase letters, postal codes to their 5 digit prefix. Sources routinely carry more
    than one email or phone per person, so those are sets.
    """

    emails: frozenset[str] = field(default_factory=frozenset)
    phones: frozenset[str] = field(default_factory=frozenset)
    first_name: str = ""
    last_name: str = ""
    zip5: str | None = None

    @property
    def name(self) -> tuple[str, str] | None:
        """The (first, last) name pair, or None if either half is missing."""
        if self.first_name and self.last_name:
            return self.first_name, self.last_name
        return None

    @property
    def is_empty(self) -> bool:
        """True if there is nothing here to match on."""
        return not (self.emails or self.phones or self.name)


def contact_keys(
    *,
    emails: Iterable[str | None] | str | None = None,
    phones: Iterable[str | None] | str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    full_name: str | None = None,
    postal_code: str | None = None,
    expand_email_subaddress: bool = True,
) -> ContactKeys:
    """
    Build normalized ContactKeys from whatever raw values a source provides.

    params:
        emails: one email or an iterable of them; blanks and duplicates are dropped
        phones: one phone or an iterable of them, in any format
        first_name / last_name: name parts, if the source has them separately
        full_name: a whole name to split when first/last aren't available separately
        postal_code: ZIP or ZIP+4
        expand_email_subaddress: also index the subaddress-stripped form, so
            "a+campaign@example.com" matches "a@example.com" from the other side

    returns: normalized keys ready to index or look up
    """
    normalized_emails: set[str] = set()
    for raw in _as_iterable(emails):
        email = normalize_email(raw)
        if not email:
            continue
        normalized_emails.add(email)
        if expand_email_subaddress:
            stripped = get_email_address_without_subaddress(email)
            if stripped:
                normalized_emails.add(stripped)

    normalized_phones = {phone for raw in _as_iterable(phones) if (phone := normalize_phone(raw))}

    if (not first_name or not last_name) and full_name:
        first_name, last_name = split_name(full_name)

    return ContactKeys(
        emails=frozenset(normalized_emails),
        phones=frozenset(normalized_phones),
        first_name=normalize_name(first_name),
        last_name=normalize_name(last_name),
        zip5=normalize_zip(postal_code),
    )


def split_name(name: str | None) -> tuple[str, str]:
    """
    Split a display name into (first, last).

    Handles both "Last, First" (how VAN and many CRMs export) and "First Last". Middle names
    and multi-word surnames can't be told apart reliably, so the outer tokens are used.
    """
    if not name or not name.strip():
        return "", ""
    if "," in name:
        last, _, first = name.partition(",")
        first_tokens = first.split()
        return (first_tokens[0] if first_tokens else ""), last.strip()
    tokens = name.split()
    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return tokens[0], ""
    return tokens[0], tokens[-1]


def _as_iterable(value: Iterable[str | None] | str | None) -> Iterable[str | None]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return value
