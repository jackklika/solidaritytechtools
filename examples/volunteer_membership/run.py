"""Runner: work out the DSA membership state of every campaign volunteer, and who joined
*after* they volunteered.

Reads volunteer-list PDFs and shift-signup CSVs, collapses them into one row per distinct
person, matches each person to a Solidarity Tech user, and writes the result to parquet.

Membership state comes from the ST api rather than a json export: the api carries every user
(not just members), so we can tell "in ST but never a member" apart from "not in ST at all",
and its "join-date" property is populated for everyone with a membership status, which is what
makes the before/after question answerable.

Configure with environment variables:
    ST_API_KEY              Solidarity Tech api key
    VOLUNTEER_PDF_DIR       directory of volunteer-list PDFs
    VOLUNTEER_CSV_DIR       directory of shift-signup CSVs
    VOLUNTEER_OUTPUT_DIR    where to write parquet (default: ./volunteer_membership_output)

Writing parquet needs pandas and pyarrow, which are in the optional "analysis" extra.

Run with:
    uv run --extra analysis python examples/volunteer_membership/run.py
"""

from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Final

try:
    # we ignore[unresolved-import] because we want to ty check this file
    # even if analysis extra is not installed
    import pandas as pd  # ty: ignore[unresolved-import]
except ImportError as exc:
    raise ImportError(
        "This example needs pandas and pyarrow to write parquet. Install them with: "
        'uv sync --extra analysis (or pip install "solidaritytechtools[analysis]")'
    ) from exc

from matching import DEFAULT_CONFIDENCE_THRESHOLD, match_roster
from pdf_volunteers import count_records_in_pdf, parse_pdf_directory
from roster import BOTH_SOURCES, CSV_ONLY_SOURCE, PDF_ONLY_SOURCE, Volunteer, build_roster
from shift_signups import parse_csv_directory

from solidaritytechtools.services.users import UserStore
from solidaritytechtools.utils.membership import (
    MEMBER_IN_GOOD_STANDING_LABEL,
    get_join_date,
    get_membership_status,
    get_membership_type,
    get_monthly_dues_status,
)

logger = logging.getLogger(__name__)

API_KEY: Final[str] = os.environ.get("ST_API_KEY", "")
PDF_DIR: Final[str] = os.environ.get("VOLUNTEER_PDF_DIR", "")
CSV_DIR: Final[str] = os.environ.get("VOLUNTEER_CSV_DIR", "")
OUTPUT_DIR: Final[Path] = Path(
    os.environ.get("VOLUNTEER_OUTPUT_DIR", "volunteer_membership_output")
)

VOLUNTEERS_PARQUET: Final[str] = "volunteers.parquet"
SHIFTS_PARQUET: Final[str] = "volunteer_shifts.parquet"

NOT_IN_ST: Final[str] = "Not in Solidarity Tech"
IN_ST_NEVER_MEMBER: Final[str] = "In ST, never a member"

# Columns built from optional python values land as `object` unless given explicit dtypes.
_DATE_COLUMNS: Final[tuple[str, ...]] = (
    "first_completed_shift",
    "last_completed_shift",
    "join_date",
    "shift_date",
    "signup_date",
)
_NULLABLE_BOOL_COLUMNS: Final[tuple[str, ...]] = (
    "was_member_before_first_shift",
    "became_member_after_first_shift",
    "joined_during_or_after_campaign",
)
_NULLABLE_INT_COLUMNS: Final[tuple[str, ...]] = (
    "st_user_id",
    "age",
    "days_from_first_shift_to_join",
)


def _membership_row(volunteer: Volunteer, match: Any | None) -> dict[str, Any]:
    """Membership columns for one volunteer, given its ST match (if any)."""
    if match is None:
        return {
            "st_user_id": None,
            "st_hash_id": None,
            "match_method": None,
            "match_confidence": None,
            "membership_state": NOT_IN_ST,
            "membership_status": None,
            "membership_type": None,
            "monthly_dues_status": None,
            "join_date": None,
            "st_created_at": None,
            "st_tags": [],
        }
    user = match.record
    status = get_membership_status(user)
    return {
        "st_user_id": user.id,
        "st_hash_id": user.hash_id,
        "match_method": match.strategy,
        "match_confidence": match.confidence,
        "membership_state": status or IN_ST_NEVER_MEMBER,
        "membership_status": status,
        "membership_type": get_membership_type(user),
        "monthly_dues_status": get_monthly_dues_status(user),
        "join_date": get_join_date(user),
        "st_created_at": user.created_at,
        "st_tags": list(user.tags),
    }


def build_dataframes(
    roster: list[Volunteer],
    matches: dict[int, Any],
    *,
    campaign_start: date | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the per-volunteer and per-shift dataframes."""
    volunteer_rows: list[dict[str, Any]] = []
    shift_rows: list[dict[str, Any]] = []

    for position, volunteer in enumerate(roster):
        match = matches.get(position)
        membership = _membership_row(volunteer, match)
        join_date = membership["join_date"]
        first_shift = volunteer.first_completed_shift

        became_member_after: bool | None = None
        was_member_before: bool | None = None
        days_to_join: int | None = None
        if join_date is not None and first_shift is not None:
            became_member_after = join_date > first_shift
            was_member_before = not became_member_after
            days_to_join = (join_date - first_shift).days

        joined_during_or_after_campaign: bool | None = None
        if join_date is not None and campaign_start is not None:
            joined_during_or_after_campaign = join_date >= campaign_start

        volunteer_rows.append(
            {
                "volunteer_index": position,
                "first_name": volunteer.first_name,
                "last_name": volunteer.last_name,
                "name": volunteer.name,
                "van_id": volunteer.van_id,
                "email": volunteer.email,
                "phones": sorted(volunteer.phones),
                "city": volunteer.city,
                "state": volunteer.state,
                "zip5": volunteer.zip5,
                "age": volunteer.age,
                "sex": volunteer.sex,
                "regions": sorted(volunteer.regions),
                "source": volunteer.source,
                "source_pdfs": sorted(volunteer.source_pdfs),
                "n_shifts_completed": volunteer.n_shifts_completed,
                "n_signups": volunteer.n_signups,
                "first_completed_shift": first_shift,
                "last_completed_shift": volunteer.last_completed_shift,
                "roles": volunteer.roles,
                **membership,
                "is_member": membership["membership_status"] == MEMBER_IN_GOOD_STANDING_LABEL,
                "was_member_before_first_shift": was_member_before,
                "became_member_after_first_shift": became_member_after,
                "days_from_first_shift_to_join": days_to_join,
                "joined_during_or_after_campaign": joined_during_or_after_campaign,
            }
        )

        for shift in volunteer.shifts:
            shift_rows.append(
                {
                    "volunteer_index": position,
                    "van_id": shift.van_id,
                    "event": shift.event,
                    "shift_date": shift.shift_date,
                    "location": shift.location,
                    "role": shift.role,
                    "status": shift.status,
                    "completed": shift.completed,
                    "recruited_by": shift.recruited_by,
                    "signup_date": shift.signup_date,
                    "source_file": shift.source_file,
                }
            )

    return _normalize_dtypes(pd.DataFrame(volunteer_rows)), _normalize_dtypes(
        pd.DataFrame(shift_rows)
    )


def _normalize_dtypes(frame: pd.DataFrame) -> pd.DataFrame:
    """Give date, nullable-bool and nullable-int columns real dtypes instead of object."""
    for column in _DATE_COLUMNS:
        if column in frame:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    for column in _NULLABLE_BOOL_COLUMNS:
        if column in frame:
            frame[column] = frame[column].astype("boolean")
    for column in _NULLABLE_INT_COLUMNS:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")
    if "st_created_at" in frame:
        # Timestamps arrive with per-user utc offsets; normalize so the column is comparable.
        frame["st_created_at"] = pd.to_datetime(frame["st_created_at"], errors="coerce", utc=True)
    return frame


def _verify_pdf_extraction(pdf_dir: Path, extracted: int) -> None:
    """Cross-check the parsed record count against an independent count of the raw text."""
    expected = sum(count_records_in_pdf(path) for path in sorted(pdf_dir.glob("*.pdf")))
    if expected != extracted:
        raise ValueError(f"PDF extraction mismatch: parsed {extracted}, expected {expected}")
    logger.info(f"Verified PDF extraction: {extracted} records match the raw text count")


def print_summary(volunteers: pd.DataFrame, *, threshold: float) -> None:
    """Print the headline answers."""
    confidence = pd.to_numeric(volunteers["match_confidence"], errors="coerce").fillna(0)
    confident = volunteers[confidence >= threshold]
    did_volunteer = volunteers[volunteers["n_shifts_completed"] > 0]
    confirmed = did_volunteer[confidence.loc[did_volunteer.index] >= threshold]

    print(f"\n{'=' * 78}\nROSTER\n{'=' * 78}")
    print(f"  distinct volunteers            {len(volunteers):>6}")
    for label, source in (
        ("  in PDFs and CSVs", BOTH_SOURCES),
        ("  in shift CSVs only", CSV_ONLY_SOURCE),
        ("  in volunteer PDFs only", PDF_ONLY_SOURCE),
    ):
        print(f"  {label:<30} {int((volunteers['source'] == source).sum()):>6}")
    print(f"  completed >=1 shift            {len(did_volunteer):>6}")

    print(f"\n{'=' * 78}\nST MATCHING\n{'=' * 78}")
    matched = volunteers["st_user_id"].notna().sum()
    print(f"  matched to an ST user          {int(matched):>6} / {len(volunteers)}")
    for method, count in volunteers["match_method"].value_counts().items():
        print(f"    by {str(method):<26} {int(count):>6}")
    print(f"  at confidence >= {threshold}          {len(confident):>6}")

    print(f"\n{'=' * 78}\nMEMBERSHIP STATE - volunteers who completed >=1 shift\n{'=' * 78}")
    print(f"  cohort: {len(did_volunteer)} people who actually volunteered\n")
    states = did_volunteer["membership_state"].value_counts()
    for state, count in states.items():
        share = 100 * count / len(did_volunteer)
        print(f"  {str(state):<34} {int(count):>6}  ({share:5.1f}%)")

    print(f"\n{'=' * 78}\nVOLUNTEERED, THEN JOINED DSA\n{'=' * 78}")
    print(f"  (confidence >= {threshold}, and both a shift date and a join date are known)")
    dated = confirmed[confirmed["became_member_after_first_shift"].notna()]
    # The column holds True/False/None, so it is object dtype; cast before negating, or `~`
    # applies Python's bitwise-not to the bools and yields -1/-2 instead of a mask.
    joined_after = dated["became_member_after_first_shift"].astype(bool)
    after = dated[joined_after]
    before = dated[~joined_after]
    print(f"  comparable people              {len(dated):>6}")
    print(f"  already members before         {len(before):>6}")
    print(f"  JOINED AFTER VOLUNTEERING      {len(after):>6}")
    if len(after):
        days = pd.to_numeric(after["days_from_first_shift_to_join"], errors="coerce")
        print(f"    days from shift to joining:  median {days.median():.0f}, max {days.max():.0f}")
        print("\n  by membership status now:")
        for status, count in after["membership_status"].value_counts().items():
            print(f"    {str(status):<32} {int(count):>6}")

    print(f"\n{'=' * 78}\nUNMATCHED RATE BY REGION (high = needs that chapter's data)\n{'=' * 78}")
    exploded = volunteers.explode("regions").dropna(subset=["regions"])
    for region, group in exploded.groupby("regions"):
        unmatched = group["st_user_id"].isna().sum()
        print(
            f"  {str(region):<16} {int(unmatched):>5} unmatched / {len(group):>5} "
            f"({100 * unmatched / len(group):5.1f}%)"
        )


def run(*, write_parquet: bool = True, threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> None:
    if not API_KEY:
        raise ValueError("Set ST_API_KEY")
    if not PDF_DIR or not CSV_DIR:
        raise ValueError("Set VOLUNTEER_PDF_DIR and VOLUNTEER_CSV_DIR")

    pdf_dir = Path(PDF_DIR)
    pdf_records = parse_pdf_directory(pdf_dir)
    _verify_pdf_extraction(pdf_dir, len(pdf_records))
    signups = parse_csv_directory(CSV_DIR)
    logger.info(f"Parsed {len(pdf_records)} PDF records and {len(signups)} signup rows")

    roster = build_roster(pdf_records, signups)

    completed_dates = [s.shift_date for s in signups if s.completed and s.shift_date]
    campaign_start = min(completed_dates) if completed_dates else None
    logger.info(f"Campaign window starts {campaign_start}")

    store = UserStore.from_api(API_KEY)
    logger.info(f"Loaded {len(store.users)} ST users")
    matches = match_roster(roster, store.users)

    volunteers, shifts = build_dataframes(roster, matches, campaign_start=campaign_start)
    print_summary(volunteers, threshold=threshold)

    if write_parquet:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        volunteers.to_parquet(OUTPUT_DIR / VOLUNTEERS_PARQUET, index=False)
        shifts.to_parquet(OUTPUT_DIR / SHIFTS_PARQUET, index=False)
        print(f"\nWrote {OUTPUT_DIR / VOLUNTEERS_PARQUET} ({len(volunteers)} rows)")
        print(f"Wrote {OUTPUT_DIR / SHIFTS_PARQUET} ({len(shifts)} rows)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run()
