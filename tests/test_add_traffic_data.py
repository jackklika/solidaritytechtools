from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import httpx

import solidaritytechtools.tools.add_traffic_data as mod
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.client.models import Address, User
from solidaritytechtools.tools.add_traffic_data import (
    TRAFFIC_SCORE_PROPERTY,
    add_traffic_data,
    build_traffic_scorer,
    format_address,
    get_coordinates,
    is_member_in_good_standing,
    is_sign_visible_road,
    score_contacts,
)
from solidaritytechtools.utils.traffic_score import TrafficScorer

MIGS = [{"label": "Member in Good Standing", "value": "AfVqfj0n"}]


def _user(
    user_id: int,
    *,
    lat: float | None = None,
    lon: float | None = None,
    migs: bool = False,
    hash_id: str | None = None,
) -> User:
    address = Address(latitude=lat, longitude=lon) if lat is not None and lon is not None else None
    props = {"membership-status": MIGS if migs else []}
    return User(id=user_id, hash_id=hash_id, address=address, custom_user_properties=props)


def _scorer(tmp_path: Path, points: dict[tuple[float, float], int]) -> TrafficScorer:
    """A real TrafficScorer over a small GeoJSON fixture, one count point per (lat, lon)."""
    features = [_feature(lon, lat, aadt, "MAIN ST") for (lat, lon), aadt in points.items()]
    path = tmp_path / "counts.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    return TrafficScorer(path)


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> STClient:
    """A real STClient whose HTTP layer is served by `handler` instead of the network."""
    return STClient(api_key="x", transport=httpx.MockTransport(handler))


def test_is_member_in_good_standing() -> None:
    assert is_member_in_good_standing(_user(1, migs=True))
    assert not is_member_in_good_standing(_user(2, migs=False))
    other = User(id=3, custom_user_properties={"membership-status": [{"value": "ZZZ"}]})
    assert not is_member_in_good_standing(other)
    assert not is_member_in_good_standing(User(id=4))


def test_get_coordinates() -> None:
    assert get_coordinates(_user(1, lat=43.0, lon=-88.0)) == (43.0, -88.0)
    assert get_coordinates(_user(2)) is None
    assert get_coordinates(User(id=3, address=Address(latitude=43.0))) is None


def test_score_contacts_counts_and_sorting(tmp_path: Path) -> None:
    users = [
        _user(1, lat=43.0, lon=-88.0, hash_id="hash-1"),  # busy road
        _user(2, lat=44.0, lon=-89.0),  # quiet road
        _user(3, lat=45.0, lon=-90.0),  # no traffic data
        _user(4),  # no coordinates
    ]
    scorer = _scorer(tmp_path, {(43.0, -88.0): 20000, (44.0, -89.0): 500})

    result = score_contacts(users, scorer)

    assert result.considered == 4
    assert result.no_coordinates == 1
    assert result.no_traffic_data == 1
    assert [c.user_id for c in result.scored] == [1, 2]  # sorted by aadt desc
    assert result.scored[0].aadt == 20000
    assert result.scored[0].hash_id == "hash-1"
    assert result.scored[0].address is not None
    assert result.scored[0].address.latitude == 43.0


def test_format_address() -> None:
    full = Address(address1="123 Main St", city="Madison", state="WI", zip_code="53703")
    assert format_address(full) == "123 Main St, Madison, WI 53703"
    assert format_address(Address(city="Madison", state="WI")) == "Madison, WI"
    assert format_address(None) == ""


def test_score_contacts_migs_filter(tmp_path: Path) -> None:
    users = [_user(1, lat=43.0, lon=-88.0, migs=True), _user(2, lat=43.0, lon=-88.0, migs=False)]
    scorer = _scorer(tmp_path, {(43.0, -88.0): 1000})

    result = score_contacts(users, scorer, members_in_good_standing_only=True)

    assert result.considered == 1
    assert [c.user_id for c in result.scored] == [1]


class _FakeStore:
    def __init__(self, users: list[User]):
        self.users = users


def test_add_traffic_data_writes(monkeypatch, tmp_path: Path) -> None:
    users = [_user(1, lat=43.0, lon=-88.0)]
    monkeypatch.setattr(
        mod.UserStore, "from_api", classmethod(lambda cls, *a, **k: _FakeStore(users))
    )
    sent: list[tuple[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append((request.url.path, json.loads(request.content)))
        return httpx.Response(200, json={"data": {"id": 1}})

    monkeypatch.setattr(mod, "STClient", lambda *a, **k: _client(handler))

    result = add_traffic_data(api_key="x", scorer=_scorer(tmp_path, {(43.0, -88.0): 7500}))

    assert result.updated == 1
    assert result.failed == 0
    path, body = sent[0]
    assert path.endswith("/users/1")
    assert body == {"custom_user_properties": {TRAFFIC_SCORE_PROPERTY: "7500"}}


def test_add_traffic_data_dry_run_writes_nothing(monkeypatch, tmp_path: Path) -> None:
    users = [_user(1, lat=43.0, lon=-88.0)]
    monkeypatch.setattr(
        mod.UserStore, "from_api", classmethod(lambda cls, *a, **k: _FakeStore(users))
    )
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request.url.path)
        return httpx.Response(200, json={"data": {"id": 1}})

    monkeypatch.setattr(mod, "STClient", lambda *a, **k: _client(handler))

    result = add_traffic_data(
        api_key="x", dry_run=True, scorer=_scorer(tmp_path, {(43.0, -88.0): 7500})
    )

    assert result.num_scored == 1
    assert result.updated == 0
    assert sent == []


def test_is_sign_visible_road() -> None:
    assert is_sign_visible_road("STH 100 BTWN POTTER & WISCONSIN", 38000)  # surface arterial
    assert not is_sign_visible_road("I-94 BTWN 35TH & 28TH STS", 160000)  # interstate
    assert not is_sign_visible_road("SB LANES OF I-43 THROUGH HILLSIDE", 72700)  # I-43 mid-string
    assert not is_sign_visible_road("OFF RAMP FROM STH 13 TO STH 29", 2500)  # ramp
    assert not is_sign_visible_road("USH 12/14/18/151 BELTLINE", 125000)  # over the AADT cap
    # Name-parsing alone can't catch a US-highway freeway; the cap is what does.
    assert is_sign_visible_road("USH 12/14/18/151 BELTLINE", 125000, max_aadt=None)
    assert not is_sign_visible_road("CTH O MOORLAND RD", 38000, max_aadt=30000)  # stricter cap


def _feature(lon: float, lat: float, aadt: int, desc: str) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "RDWY_AADT": aadt,
            "AADT_RPTG_YR": 2024,
            "TRFC_PT_LOC_DESC": desc,
            "COUNTY_NAME": "Test",
        },
    }


def test_build_traffic_scorer_filters_freeways(tmp_path) -> None:
    geojson = {
        "type": "FeatureCollection",
        "features": [
            _feature(-88.0, 43.0, 5000, "MAIN ST"),  # keep
            _feature(-88.1, 43.1, 160000, "I-94 BTWN 35TH & 28TH"),  # drop: interstate
            _feature(-88.2, 43.2, 2000, "OFF RAMP FROM STH 13"),  # drop: ramp
            _feature(-88.3, 43.3, 125000, "USH 12/14/18/151 BELTLINE"),  # drop: over cap
        ],
    }
    path = tmp_path / "counts.geojson"
    path.write_text(json.dumps(geojson))

    scorer = build_traffic_scorer(path)
    assert {point.location for point in scorer.points} == {"MAIN ST"}

    unfiltered = build_traffic_scorer(path, exclude_freeways=False, max_aadt=None)
    assert len(unfiltered.points) == 4
