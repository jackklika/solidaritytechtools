"""Score Solidarity Tech contacts by nearby traffic (AADT) and write it back as a
custom user property, for building yard-sign prioritization pull lists.

Loads all users once, optionally filters to Members in Good Standing, snaps each
contact's address coordinates to the nearest WisDOT traffic count (see
solidaritytechtools.utils.traffic_score), and writes the AADT to a custom user
property (TRAFFIC_SCORE_PROPERTY). Supports dry runs.

By default, freeways and ramps are excluded from the count points (see
build_traffic_scorer) so homes snap to the nearest sign-visible surface street
rather than a nearby freeway no driver could read a yard sign from.

The target custom property must already exist in your ST instance (a "number" or
"input" field); create it in the ST UI or via client.create_custom_user_property
and set its key as TRAFFIC_SCORE_PROPERTY.
"""

from __future__ import annotations

import json
import logging
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import Any, Final

from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.client.models import Address, User, UserUpdate
from solidaritytechtools.services.users import UserStore
from solidaritytechtools.utils.traffic_score import (
    DEFAULT_MAX_DISTANCE_M,
    CountPoint,
    TrafficScore,
    TrafficScorer,
)

logger = logging.getLogger(__name__)

# Custom user property (key/slug) the AADT score is written to. Must already exist
# in your ST instance as a number/input field.
TRAFFIC_SCORE_PROPERTY: Final[str] = "traffic-aadt"

# "Member in Good Standing" lives as an option in the "membership-status" property.
MEMBERSHIP_STATUS_PROPERTY: Final[str] = "membership-status"
MEMBER_IN_GOOD_STANDING_VALUE: Final[str] = "AfVqfj0n"

# Count points at/above this AADT are treated as freeway-grade. Surface streets where
# a yard sign is legible top out around here; freeway-grade US/State highways (e.g. the
# Madison Beltline, Stadium Freeway) carry higher counts but aren't labeled interstates.
DEFAULT_MAX_AADT: Final[int] = 40_000

# Interstate ("I-94", "...I-43...") or ramp count points, from the location description.
_FREEWAY_LOC_RE: Final[re.Pattern[str]] = re.compile(r"\bRAMP\b|\bIH?[\s-]?\d")


@dataclass(frozen=True)
class ScoredContact:
    user_id: int
    hash_id: str | None  # ST hash id, easier to search/link by than the integer id
    aadt: int
    score: TrafficScore
    address: Address | None  # the member's address (carries street fields + lat/lon)


@dataclass
class AddTrafficResult:
    considered: int  # contacts examined (after the optional MIGS filter)
    no_coordinates: int  # skipped: no lat/lon on the address
    no_traffic_data: int  # scored, but nearest count point was too far
    scored: list[ScoredContact]  # got an AADT, sorted highest-first
    updated: int = 0  # successfully written to ST (0 on a dry run)
    failed: int = 0  # update raised

    @property
    def num_scored(self) -> int:
        return len(self.scored)


def is_member_in_good_standing(user: User) -> bool:
    """True if the user's membership-status property includes "Member in Good Standing"."""
    prop = (user.custom_user_properties or {}).get(MEMBERSHIP_STATUS_PROPERTY)
    if isinstance(prop, list):
        return any(
            isinstance(item, dict) and item.get("value") == MEMBER_IN_GOOD_STANDING_VALUE
            for item in prop
        )
    return False


def get_coordinates(user: User) -> tuple[float, float] | None:
    """Return (lat, lon) from the user's address, or None if unavailable."""
    address = user.address
    if address is None or address.latitude is None or address.longitude is None:
        return None
    return address.latitude, address.longitude


def get_street_hint(user: User) -> str | None:
    """The member's street line (e.g. "111 N Milwaukee St") for on-street matching.

    Passing this to the scorer is what keeps a side-street home from inheriting a busy
    parallel road's count: without it, plain nearest-snap credits a quiet street with
    the nearest arterial within range. Returns None when no street is on file.
    """
    address = user.address
    return address.address1 if address and address.address1 else None


def format_address(address: Address | None) -> str:
    """Compact single-line address, e.g. '123 Main St, Madison, WI 53703'."""
    if address is None:
        return ""
    line = ", ".join(part for part in (address.address1, address.city, address.state) if part)
    if address.zip_code:
        line = f"{line} {address.zip_code}".strip()
    return line


def is_freeway_location(location: str) -> bool:
    """Heuristic: True if a count point's WisDOT description is an interstate or a ramp."""
    return bool(_FREEWAY_LOC_RE.search((location or "").upper()))


def is_sign_visible_road(
    location: str,
    aadt: int,
    *,
    exclude_freeways: bool = True,
    max_aadt: int | None = DEFAULT_MAX_AADT,
) -> bool:
    """
    Whether a traffic count point is a surface road where a yard sign is legible.

    Freeways carry the highest AADT but no one reads a sign at highway speed, and a home near a
    freeway snaps to it even when it actually fronts a quiet street. We drop interstates and ramps
    by name, plus anything above max_aadt (which catches freeway-grade US/State highways such as
    the Madison Beltline that name-parsing alone misses).
    """
    if exclude_freeways and is_freeway_location(location):
        return False
    if max_aadt is not None and aadt > max_aadt:
        return False
    return True


def _points_to_geojson(points: list[CountPoint]) -> dict[str, Any]:
    """Serialize count points back to the WisDOT GeoJSON shape TrafficScorer reads."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [point.lon, point.lat]},
                "properties": {
                    "RDWY_AADT": point.aadt,
                    "AADT_RPTG_YR": point.year,
                    "TRFC_PT_LOC_DESC": point.location,
                    "COUNTY_NAME": point.county,
                },
            }
            for point in points
        ],
    }


def build_traffic_scorer(
    geojson_path: Path | None = None,
    *,
    exclude_freeways: bool = True,
    max_aadt: int | None = DEFAULT_MAX_AADT,
) -> TrafficScorer:
    """
    Build a TrafficScorer whose count points exclude freeways, so addresses snap to the nearest
    sign-visible surface street instead of a nearby freeway.

    Filtering the count points (not the results) is what matters: a freeway-adjacent home re-snaps
    to its real street rather than being dropped. Pass exclude_freeways=False and max_aadt=None for
    the unfiltered scorer.
    """
    base = TrafficScorer(geojson_path)
    if not exclude_freeways and max_aadt is None:
        return base

    kept = [
        point
        for point in base.points
        if is_sign_visible_road(
            point.location, point.aadt, exclude_freeways=exclude_freeways, max_aadt=max_aadt
        )
    ]
    logger.info(f"Sign-visible count points: {len(kept)} of {len(base.points)}")
    cache_path = Path(tempfile.gettempdir()) / "widot_sign_visible.geojson"
    cache_path.write_text(json.dumps(_points_to_geojson(kept)))
    return TrafficScorer(geojson_path=cache_path)


def score_contacts(
    users: list[User],
    scorer: TrafficScorer,
    *,
    max_distance_m: float = DEFAULT_MAX_DISTANCE_M,
    members_in_good_standing_only: bool = False,
) -> AddTrafficResult:
    """Score each contact's address; no API writes. Pure and order-stable by AADT desc."""
    if members_in_good_standing_only:
        users = [user for user in users if is_member_in_good_standing(user)]

    scored: list[ScoredContact] = []
    no_coordinates = 0
    no_traffic_data = 0
    for user in users:
        coordinates = get_coordinates(user)
        if coordinates is None:
            no_coordinates += 1
            continue
        score = scorer.score(
            *coordinates, street_hint=get_street_hint(user), max_distance_m=max_distance_m
        )
        if score.aadt is None:
            no_traffic_data += 1
            continue
        scored.append(
            ScoredContact(
                user_id=user.id,
                hash_id=user.hash_id,
                aadt=score.aadt,
                score=score,
                address=user.address,
            )
        )

    scored.sort(key=lambda contact: contact.aadt, reverse=True)
    return AddTrafficResult(
        considered=len(users),
        no_coordinates=no_coordinates,
        no_traffic_data=no_traffic_data,
        scored=scored,
    )


def add_traffic_data(
    *,
    api_key: str,
    members_in_good_standing_only: bool = False,
    max_distance_m: float = DEFAULT_MAX_DISTANCE_M,
    exclude_freeways: bool = True,
    max_aadt: int | None = DEFAULT_MAX_AADT,
    dry_run: bool = False,
    refresh: bool = False,
    property_key: str = TRAFFIC_SCORE_PROPERTY,
    delay_s: float = 0.0,
    geojson_path: Path | None = None,
    scorer: TrafficScorer | None = None,
) -> AddTrafficResult:
    """
    Fetch all contacts, score them by nearby traffic, and write the AADT to a custom property.

    params:
        api_key: api key to auth with ST
        members_in_good_standing_only: only score Members in Good Standing
        max_distance_m: max snap distance to a count point before it's "no data"
        exclude_freeways: drop interstate/ramp count points so homes snap to surface streets
        max_aadt: also drop count points above this AADT (freeway-grade); None to disable
        dry_run: if True, score and report but write nothing
        refresh: if True, re-fetch users instead of using the on-disk cache
        property_key: custom property (key/slug) to write the AADT to
        delay_s: optional pause between writes to avoid rate limits
        geojson_path: local WisDOT GeoJSON to score against; downloaded if None
        scorer: a prebuilt TrafficScorer; if given, exclude_freeways/max_aadt/geojson_path are
            ignored (you control the count points)

    returns: an AddTrafficResult with counts and the scored contacts (AADT desc)
    """
    store = UserStore.from_api(api_key, refresh=refresh)
    if scorer is None:
        scorer = build_traffic_scorer(
            geojson_path, exclude_freeways=exclude_freeways, max_aadt=max_aadt
        )
    logger.info(
        f"Scoring traffic for {len(store.users)} contacts "
        f"(migs_only={members_in_good_standing_only}, dry_run={dry_run})"
    )

    result = score_contacts(
        store.users,
        scorer,
        max_distance_m=max_distance_m,
        members_in_good_standing_only=members_in_good_standing_only,
    )
    logger.info(
        f"considered={result.considered} scored={result.num_scored} "
        f"no_coords={result.no_coordinates} no_data={result.no_traffic_data}"
    )

    if dry_run:
        logger.info(f"[DRY RUN] Would write {property_key} to {result.num_scored} contacts.")
        return result

    with STClient(api_key=api_key) as client:
        for contact in result.scored:
            try:
                if delay_s:
                    sleep(delay_s)
                client.update_user(
                    contact.user_id,
                    UserUpdate(custom_user_properties={property_key: str(contact.aadt)}),
                )
                result.updated += 1
            except Exception:
                logger.exception(f"Failed to write traffic score for user {contact.user_id}")
                result.failed += 1

    logger.info(f"Wrote {property_key} to {result.updated} contacts ({result.failed} failed).")
    return result
