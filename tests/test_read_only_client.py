from __future__ import annotations

import httpx
import pytest

from solidaritytechtools.client.base_client import (
    READ_ONLY_ENV_VAR,
    STClient,
    STReadOnlyError,
)


@pytest.fixture(autouse=True)
def _clear_read_only_env(monkeypatch) -> None:
    """The env var forces read-only on, so a developer's shell must not leak into these tests."""
    monkeypatch.delenv(READ_ONLY_ENV_VAR, raising=False)


def _recording_transport(seen: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": {"id": 1}})

    return httpx.MockTransport(handler)


def test_read_only_blocks_every_write_verb() -> None:
    with STClient(api_key="x", read_only=True) as client:
        for call in (
            lambda: client._post("/users", json={"chapter_id": 1}),
            lambda: client._put("/users/1", json={"first_name": "a"}),
            lambda: client._delete("/user_lists/1"),
        ):
            with pytest.raises(STReadOnlyError):
                call()


def test_no_write_reaches_the_transport() -> None:
    seen: list[httpx.Request] = []
    with STClient(api_key="x", transport=_recording_transport(seen), read_only=True) as client:
        with pytest.raises(STReadOnlyError):
            client.create_user({"chapter_id": 1, "phone_number": "5555555555"})
        with pytest.raises(STReadOnlyError):
            client.delete_user_list(1)

    assert seen == []


def test_read_only_blocks_direct_use_of_the_underlying_httpx_client() -> None:
    """The _request guard is bypassable via client.client; the transport guard is not."""
    seen: list[httpx.Request] = []
    with STClient(api_key="x", transport=_recording_transport(seen), read_only=True) as client:
        with pytest.raises(STReadOnlyError):
            client.client.post("/users", json={"chapter_id": 1})

    assert seen == []


def test_reads_still_work_when_read_only() -> None:
    seen: list[httpx.Request] = []
    with STClient(api_key="x", transport=_recording_transport(seen), read_only=True) as client:
        client._get("/users", params={"_limit": 1})

    assert [r.method for r in seen] == ["GET"]


def test_writes_are_allowed_by_default() -> None:
    seen: list[httpx.Request] = []
    with STClient(api_key="x", transport=_recording_transport(seen)) as client:
        assert client.read_only is False
        client._post("/users", json={"chapter_id": 1})

    assert [r.method for r in seen] == ["POST"]


def test_env_var_forces_read_only(monkeypatch) -> None:
    monkeypatch.setenv(READ_ONLY_ENV_VAR, "1")
    with STClient(api_key="x") as client:
        assert client.read_only is True
        with pytest.raises(STReadOnlyError):
            client._post("/users", json={"chapter_id": 1})


def test_env_var_cannot_disable_read_only(monkeypatch) -> None:
    monkeypatch.setenv(READ_ONLY_ENV_VAR, "0")
    with STClient(api_key="x", read_only=True) as client:
        assert client.read_only is True


def test_read_only_flag_cannot_be_unset_at_runtime() -> None:
    with STClient(api_key="x", read_only=True) as client:
        with pytest.raises(AttributeError):
            client.read_only = False  # type: ignore[misc]
        assert client.read_only is True
