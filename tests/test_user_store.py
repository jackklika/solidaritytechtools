from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import httpx

from solidaritytechtools.client import models as client_models
from solidaritytechtools.client.base_client import STClient
from solidaritytechtools.services.users import UserStore, get_all_users, set_email_permission
from solidaritytechtools.utils.emails import normalize_email


def _user(
    user_id: int, email: str | None = None, created_at: datetime | None = None
) -> client_models.User:
    return client_models.User(id=user_id, email=email, created_at=created_at)


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> STClient:
    """A real STClient whose HTTP layer is served by `handler` instead of the network."""
    return STClient(api_key="x", transport=httpx.MockTransport(handler))


def test_normalize_email() -> None:
    assert normalize_email("  Jack@Example.COM ") == "jack@example.com"
    assert normalize_email("") is None
    assert normalize_email(None) is None


def test_get_all_users_paginates() -> None:
    users = [{"id": i, "email": f"u{i}@example.com"} for i in range(5)]
    requested: list[tuple[int, int]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        limit = int(request.url.params["_limit"])
        offset = int(request.url.params["_offset"])
        requested.append((limit, offset))
        page = users[offset : offset + limit]
        return httpx.Response(200, json={"data": page, "meta": {"total_count": len(users)}})

    result = get_all_users(_client(handler), page_size=2)

    assert [u.id for u in result] == [0, 1, 2, 3, 4]
    assert requested[0] == (2, 0)


def test_match_email_exact_is_case_and_whitespace_insensitive() -> None:
    store = UserStore([_user(1, "Jack@Example.com")])
    matched = store.match_email("  jack@example.COM ")
    assert matched is not None
    assert matched.id == 1
    assert store.match_email("nobody@example.com") is None


def test_match_email_input_has_subaddress_account_is_bare() -> None:
    store = UserStore([_user(1, "jack@example.com")])
    matched = store.match_email("jack+newsletter@example.com")
    assert matched is not None
    assert matched.id == 1


def test_match_email_account_has_subaddress_input_is_bare() -> None:
    store = UserStore([_user(1, "jack+promo@example.com")])
    matched = store.match_email("jack@example.com")
    assert matched is not None
    assert matched.id == 1


def test_match_email_subaddress_stripping_can_be_disabled() -> None:
    store = UserStore([_user(1, "jack@example.com")])
    assert store.match_email("jack+x@example.com", strip_subaddress=False) is None


def test_match_email_multiple_matches_picks_newest() -> None:
    older = _user(1, "jack@example.com", datetime(2020, 1, 1))
    newer = _user(2, "jack+a@example.com", datetime(2023, 1, 1))
    store = UserStore([older, newer])

    # "jack+b" matches neither exactly; both strip to jack@example.com, newest wins.
    matched = store.match_email("jack+b@example.com")
    assert matched is not None
    assert matched.id == 2


def test_match_emails_keys_by_original_and_skips_misses() -> None:
    store = UserStore([_user(1, "jack@example.com")])

    result = store.match_emails(["Jack@example.com", "missing@example.com", ""])

    assert result == {"Jack@example.com": 1}


def test_store_cache_round_trip(tmp_path: Path) -> None:
    users = [_user(1, "jack@example.com", datetime(2021, 5, 1)), _user(2, "jill@example.com")]
    cache = tmp_path / "users.json"

    UserStore(users).save(cache)
    loaded = UserStore.load(cache)

    assert [u.id for u in loaded.users] == [1, 2]
    matched = loaded.match_email("jack@example.com")
    assert matched is not None
    assert matched.id == 1


def test_set_email_permission_records_success_and_failure() -> None:
    sent: list[tuple[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append((request.url.path, json.loads(request.content)))
        if request.url.path.endswith("/2"):
            return httpx.Response(500, json={"error": "boom"})
        return httpx.Response(200, json={"data": {"id": 1}})

    results = set_email_permission(_client(handler), [1, 2], permission=False)

    assert results == {1: True, 2: False}
    assert sent[0][0].endswith("/users/1")
    assert sent[0][1] == {"email_permission": False}
