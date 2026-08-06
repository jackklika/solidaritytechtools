from __future__ import annotations

from datetime import datetime
from pathlib import Path

from solidaritytechtools.client import models as client_models
from solidaritytechtools.services.users import UserStore, get_all_users, set_email_permission
from solidaritytechtools.utils.emails import normalize_email


def _user(
    user_id: int, email: str | None = None, created_at: datetime | None = None
) -> client_models.User:
    return client_models.User(id=user_id, email=email, created_at=created_at)


class _StubListClient:
    """Minimal stand-in for STClient.get_users used by get_all_users."""

    def __init__(self, users: list[client_models.User]):
        self._users = users
        self.calls: list[tuple[int, int]] = []

    def get_users(
        self, limit: int = 20, offset: int = 0, since: int = 0, **kwargs: object
    ) -> client_models.PaginatedResponse[client_models.User]:
        self.calls.append((limit, offset))
        page = self._users[offset : offset + limit]
        meta = client_models.PaginationMeta(
            total_count=len(self._users), limit=limit, offset=offset
        )
        return client_models.PaginatedResponse[client_models.User](data=page, meta=meta)


class _StubUpdateClient:
    """Minimal stand-in for STClient.update_user used by set_email_permission."""

    def __init__(self, fail_ids: set[int] | None = None):
        self.fail_ids = fail_ids or set()
        self.updates: list[tuple[int, client_models.UserUpdate]] = []

    def update_user(self, user_id: int, data: client_models.UserUpdate) -> client_models.User:
        if user_id in self.fail_ids:
            raise RuntimeError("boom")
        self.updates.append((user_id, data))
        return _user(user_id)


def test_normalize_email() -> None:
    assert normalize_email("  Jack@Example.COM ") == "jack@example.com"
    assert normalize_email("") is None
    assert normalize_email(None) is None


def test_get_all_users_paginates() -> None:
    users = [_user(i, f"u{i}@example.com") for i in range(5)]
    client = _StubListClient(users)

    result = get_all_users(client, page_size=2)

    assert [u.id for u in result] == [0, 1, 2, 3, 4]
    assert client.calls[0] == (2, 0)


def test_match_email_exact_is_case_and_whitespace_insensitive() -> None:
    store = UserStore([_user(1, "Jack@Example.com")])
    assert store.match_email("  jack@example.COM ").id == 1
    assert store.match_email("nobody@example.com") is None


def test_match_email_input_has_subaddress_account_is_bare() -> None:
    store = UserStore([_user(1, "jack@example.com")])
    assert store.match_email("jack+newsletter@example.com").id == 1


def test_match_email_account_has_subaddress_input_is_bare() -> None:
    store = UserStore([_user(1, "jack+promo@example.com")])
    assert store.match_email("jack@example.com").id == 1


def test_match_email_subaddress_stripping_can_be_disabled() -> None:
    store = UserStore([_user(1, "jack@example.com")])
    assert store.match_email("jack+x@example.com", strip_subaddress=False) is None


def test_match_email_multiple_matches_picks_newest() -> None:
    older = _user(1, "jack@example.com", datetime(2020, 1, 1))
    newer = _user(2, "jack+a@example.com", datetime(2023, 1, 1))
    store = UserStore([older, newer])

    # "jack+b" matches neither exactly; both strip to jack@example.com, newest wins.
    assert store.match_email("jack+b@example.com").id == 2


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
    assert loaded.match_email("jack@example.com").id == 1


def test_set_email_permission_records_success_and_failure() -> None:
    client = _StubUpdateClient(fail_ids={2})

    results = set_email_permission(client, [1, 2], permission=False)

    assert results == {1: True, 2: False}
    assert client.updates == [(1, client.updates[0][1])]
    assert client.updates[0][1].email_permission is False
