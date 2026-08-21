from __future__ import annotations

import csv
from pathlib import Path
from typing import Final

from solidaritytechtools.utils.emails import is_valid_email

# Fraction of a column's non-empty values that must be valid emails for it to be
# considered an email column by content (when the header name is not a clear signal).
CONTENT_EMAIL_THRESHOLD: Final[float] = 0.8


class AmbiguousEmailColumnError(Exception):
    pass


def _header_looks_like_email(header: str) -> bool:
    normalized = header.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
    return "email" in normalized


def _content_is_mostly_emails(values: list[str]) -> bool:
    if not values:
        return False
    valid = sum(1 for value in values if is_valid_email(value))
    return valid / len(values) >= CONTENT_EMAIL_THRESHOLD


def get_emails_from_csv(path: Path | str) -> list[str]:
    """
    Given a csv path, find the column that looks like an 'email addresses' column and return all
    the emails.

    The column is detected by header name first (anything containing "email"), falling back to
    column content (a column whose values are mostly valid emails) when no header matches.

    If there are multiple columns that might be email, raises AmbiguousEmailColumnError.
    Raises ValueError if no email column can be found.
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        columns: dict[str, list[str]] = {header: [] for header in headers}
        for row in reader:
            for header in headers:
                value = (row.get(header) or "").strip()
                if value:
                    columns[header].append(value)

    header_candidates = [header for header in headers if _header_looks_like_email(header)]

    if len(header_candidates) == 1:
        chosen = header_candidates[0]
    elif len(header_candidates) > 1:
        # Several email-ish headers (e.g. "email" and "email_opt_in"): keep only those whose
        # values actually look like emails to break the tie.
        refined = [h for h in header_candidates if _content_is_mostly_emails(columns[h])]
        if len(refined) != 1:
            raise AmbiguousEmailColumnError(
                f"Multiple candidate email columns by header: {header_candidates}"
            )
        chosen = refined[0]
    else:
        content_candidates = [h for h in headers if _content_is_mostly_emails(columns[h])]
        if len(content_candidates) > 1:
            raise AmbiguousEmailColumnError(
                f"Multiple columns look like emails by content: {content_candidates}"
            )
        if not content_candidates:
            raise ValueError(f"No email column found in {path}")
        chosen = content_candidates[0]

    return columns[chosen]
