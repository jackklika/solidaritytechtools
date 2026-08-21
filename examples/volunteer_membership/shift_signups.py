"""Read shift signup rows from VAN event exports.

One row per person per shift, so a volunteer appears once for every shift they signed up for.
`Status` records what actually happened (Completed, No Show, Declined, Scheduled, ...), so every
row is kept and the caller decides which statuses count as having volunteered.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Final

from solidaritytechtools.utils.emails import normalize_email
from solidaritytechtools.utils.normalize import normalize_phone

logger = logging.getLogger(__name__)

# Statuses that mean the person actually showed up and did the work.
COMPLETED_STATUSES: Final[frozenset[str]] = frozenset({"Completed", "Walk In"})

# VAN writes M/D/YYYY, and the files are UTF-8 with a BOM on the leading VanID header.
_DATE_FORMAT: Final[str] = "%m/%d/%Y"
_CSV_ENCODING: Final[str] = "utf-8-sig"


@dataclass
class ShiftSignup:
    """One person's signup for one shift."""

    van_id: str | None
    name: str
    first_name: str
    last_name: str
    email: str | None
    phones: list[str] = field(default_factory=list)
    event: str | None = None
    shift_date: date | None = None
    location: str | None = None
    role: str | None = None
    status: str | None = None
    recruited_by: str | None = None
    signup_date: date | None = None
    source_file: str = ""

    @property
    def completed(self) -> bool:
        """True if this signup means the person actually volunteered."""
        return self.status in COMPLETED_STATUSES


def parse_van_date(value: str | None) -> date | None:
    """Parse VAN's M/D/YYYY date format, returning None if absent or malformed."""
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), _DATE_FORMAT).date()
    except ValueError:
        logger.debug(f"Could not parse date {value!r}")
        return None


def split_van_name(name: str | None) -> tuple[str, str]:
    """
    Split VAN's "Last, First" display name into (first, last).

    Falls back to treating the value as "First Last" when there is no comma.
    """
    if not name or not name.strip():
        return "", ""
    if "," in name:
        last, _, first = name.partition(",")
        first_tokens = first.split()
        return (first_tokens[0] if first_tokens else ""), last.strip()
    tokens = name.split()
    if len(tokens) == 1:
        return tokens[0], ""
    return tokens[0], tokens[-1]


def parse_csv(path: Path | str) -> list[ShiftSignup]:
    """Read every signup row from one VAN event export."""
    path = Path(path)
    signups: list[ShiftSignup] = []
    with open(path, encoding=_CSV_ENCODING, newline="") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("Name") or "").strip()
            first_name, last_name = split_van_name(name)
            phones = sorted(
                {
                    phone
                    for raw in (row.get("Phone"), row.get("Cell Phone"))
                    if (phone := normalize_phone(raw))
                }
            )
            signups.append(
                ShiftSignup(
                    van_id=(row.get("VanID") or "").strip() or None,
                    name=name,
                    first_name=first_name,
                    last_name=last_name,
                    email=normalize_email(row.get("Email")),
                    phones=phones,
                    event=(row.get("Event") or "").strip() or None,
                    shift_date=parse_van_date(row.get("Date")),
                    location=(row.get("Location") or "").strip() or None,
                    role=(row.get("Role") or "").strip() or None,
                    status=(row.get("Status") or "").strip() or None,
                    recruited_by=(row.get("Recruited By") or "").strip() or None,
                    signup_date=parse_van_date(row.get("Signup Date")),
                    source_file=path.name,
                )
            )
    logger.info(f"Read {len(signups)} signup rows from {path.name}")
    return signups


def parse_csv_directory(directory: Path | str) -> list[ShiftSignup]:
    """Read signup rows from every CSV in a directory, sorted by filename."""
    paths = sorted(Path(directory).glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSVs found in {directory}")
    signups: list[ShiftSignup] = []
    for path in paths:
        signups.extend(parse_csv(path))
    return signups
