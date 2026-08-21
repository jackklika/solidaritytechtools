"""Collapse PDF volunteer lists and CSV shift signups into one row per distinct volunteer.

The same person shows up many times across the sources: once per shift in the CSVs, and once
per list in the PDFs (the "…2vol" lists overlap the full lists). The PDFs carry no VanID, so
they are linked to CSV people by shared phone number, falling back to name only when that name
is unambiguous on both sides -- common names would otherwise merge two different people.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Final

from pdf_volunteers import PdfVolunteer
from shift_signups import ShiftSignup

from solidaritytechtools.utils.normalize import normalize_name

logger = logging.getLogger(__name__)

NameKey = tuple[str, str]

PDF_ONLY_SOURCE: Final[str] = "pdf_only"
CSV_ONLY_SOURCE: Final[str] = "csv_only"
BOTH_SOURCES: Final[str] = "pdf_and_csv"


@dataclass
class Volunteer:
    """One distinct person, merged across every source they appear in."""

    first_name: str = ""
    last_name: str = ""
    name: str = ""
    van_id: str | None = None
    email: str | None = None
    phones: set[str] = field(default_factory=set)
    city: str | None = None
    state: str | None = None
    zip5: str | None = None
    age: int | None = None
    sex: str | None = None
    regions: set[str] = field(default_factory=set)
    source_pdfs: set[str] = field(default_factory=set)
    shifts: list[ShiftSignup] = field(default_factory=list)

    @property
    def name_key(self) -> NameKey:
        return normalize_name(self.first_name), normalize_name(self.last_name)

    @property
    def completed_shifts(self) -> list[ShiftSignup]:
        return [shift for shift in self.shifts if shift.completed]

    @property
    def n_shifts_completed(self) -> int:
        return len(self.completed_shifts)

    @property
    def n_signups(self) -> int:
        return len(self.shifts)

    @property
    def first_completed_shift(self) -> date | None:
        dates = [s.shift_date for s in self.completed_shifts if s.shift_date]
        return min(dates) if dates else None

    @property
    def last_completed_shift(self) -> date | None:
        dates = [s.shift_date for s in self.completed_shifts if s.shift_date]
        return max(dates) if dates else None

    @property
    def roles(self) -> list[str]:
        return sorted({s.role for s in self.completed_shifts if s.role})

    @property
    def source(self) -> str:
        if self.source_pdfs and self.shifts:
            return BOTH_SOURCES
        return PDF_ONLY_SOURCE if self.source_pdfs else CSV_ONLY_SOURCE


def _signup_identity(signup: ShiftSignup) -> str:
    """A stable key for grouping signup rows into people; VanID when present."""
    if signup.van_id:
        return f"van:{signup.van_id}"
    if signup.email:
        return f"email:{signup.email}"
    if signup.phones:
        return f"phone:{signup.phones[0]}"
    first, last = normalize_name(signup.first_name), normalize_name(signup.last_name)
    return f"name:{first}|{last}"


def _volunteers_from_signups(signups: list[ShiftSignup]) -> list[Volunteer]:
    grouped: dict[str, list[ShiftSignup]] = defaultdict(list)
    for signup in signups:
        grouped[_signup_identity(signup)].append(signup)

    volunteers: list[Volunteer] = []
    for rows in grouped.values():
        newest = max(rows, key=lambda r: r.shift_date or date.min)
        volunteer = Volunteer(
            first_name=newest.first_name,
            last_name=newest.last_name,
            name=newest.name,
            van_id=next((r.van_id for r in rows if r.van_id), None),
            email=next((r.email for r in rows if r.email), None),
            phones={phone for r in rows for phone in r.phones},
            shifts=rows,
        )
        volunteers.append(volunteer)
    return volunteers


def _merge_pdf_record(volunteer: Volunteer, record: PdfVolunteer) -> None:
    volunteer.phones.update(record.phones)
    volunteer.source_pdfs.add(record.source_file)
    if record.region:
        volunteer.regions.add(record.region)
    volunteer.city = volunteer.city or record.city
    volunteer.state = volunteer.state or record.state
    volunteer.zip5 = volunteer.zip5 or record.zip5
    volunteer.age = volunteer.age if volunteer.age is not None else record.age
    volunteer.sex = volunteer.sex or record.sex
    volunteer.name = volunteer.name or record.name


def build_roster(pdf_records: list[PdfVolunteer], signups: list[ShiftSignup]) -> list[Volunteer]:
    """
    Merge PDF and CSV sources into one row per distinct volunteer.

    params:
        pdf_records: every record parsed from the volunteer-list PDFs
        signups: every shift signup row parsed from the CSVs

    returns: the deduplicated roster
    """
    volunteers = _volunteers_from_signups(signups)

    by_phone: dict[str, Volunteer] = {}
    by_name: dict[NameKey, list[Volunteer]] = defaultdict(list)
    for volunteer in volunteers:
        for phone in volunteer.phones:
            by_phone.setdefault(phone, volunteer)
        by_name[volunteer.name_key].append(volunteer)

    # Group PDF records into people first, so the same person listed in two PDFs is one entry.
    pdf_groups: dict[tuple[NameKey, str | None], list[PdfVolunteer]] = defaultdict(list)
    for record in pdf_records:
        key = (
            (normalize_name(record.first_name), normalize_name(record.last_name)),
            record.zip5,
        )
        pdf_groups[key].append(record)

    pdf_name_counts: dict[NameKey, int] = defaultdict(int)
    for name_key, _ in pdf_groups:
        pdf_name_counts[name_key] += 1

    linked_by_phone = linked_by_name = pdf_only = 0
    for (name_key, _zip5), records in pdf_groups.items():
        phones = {phone for record in records for phone in record.phones}

        match = next((by_phone[phone] for phone in sorted(phones) if phone in by_phone), None)
        if match is not None:
            linked_by_phone += 1
        else:
            # Only trust a name link when that name is unique on both sides.
            candidates = by_name.get(name_key, [])
            if len(candidates) == 1 and pdf_name_counts[name_key] == 1 and all(name_key):
                match = candidates[0]
                linked_by_name += 1

        if match is None:
            match = Volunteer(
                first_name=records[0].first_name,
                last_name=records[0].last_name,
                name=records[0].name,
            )
            volunteers.append(match)
            pdf_only += 1

        for record in records:
            _merge_pdf_record(match, record)

    logger.info(
        f"Roster: {len(volunteers)} people "
        f"(pdf linked by phone={linked_by_phone}, by name={linked_by_name}, pdf only={pdf_only})"
    )
    return volunteers
