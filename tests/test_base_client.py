from __future__ import annotations

import pytest

import solidaritytechtools.client.base_client as bc
from solidaritytechtools.client.base_client import STClient, STRateLimitError


class _FakeResp:
    def __init__(self, status: int, headers: dict | None = None, json_data: dict | None = None):
        self.status_code = status
        self.headers = headers or {}
        self._json = json_data
        self.text = ""

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> dict:
        if self._json is None:
            raise ValueError("no json")
        return self._json


def test_retries_on_429_then_succeeds(monkeypatch) -> None:
    client = STClient(api_key="x", max_retries=3)
    calls = {"n": 0}

    def fake_request(method, path, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _FakeResp(429, headers={"Retry-After": "0"})
        return _FakeResp(200, json_data={"ok": True})

    slept: list[float] = []
    monkeypatch.setattr(client.client, "request", fake_request)
    monkeypatch.setattr(bc.time, "sleep", lambda s: slept.append(s))

    resp = client._get("/users")

    assert calls["n"] == 2  # one retry
    assert slept == [0.0]  # honored Retry-After: 0
    assert resp.is_success
    client.close()


def test_raises_after_exhausting_retries(monkeypatch) -> None:
    client = STClient(api_key="x", max_retries=2)
    calls = {"n": 0}

    def fake_request(method, path, **kwargs):
        calls["n"] += 1
        return _FakeResp(429, headers={"Retry-After": "0"}, json_data={"error": "Rate limit"})

    monkeypatch.setattr(client.client, "request", fake_request)
    monkeypatch.setattr(bc.time, "sleep", lambda s: None)

    with pytest.raises(STRateLimitError):
        client._get("/users")

    assert calls["n"] == 3  # initial + 2 retries
    client.close()


def test_retry_after_falls_back_to_exponential_backoff() -> None:
    client = STClient(api_key="x", retry_backoff_s=1.0, max_retry_wait_s=60.0)
    no_header = _FakeResp(429)
    assert client._retry_after_seconds(no_header, attempt=0) == 1.0
    assert client._retry_after_seconds(no_header, attempt=3) == 8.0
    assert client._retry_after_seconds(no_header, attempt=10) == 60.0  # capped
    assert client._retry_after_seconds(_FakeResp(429, {"Retry-After": "30"}), attempt=0) == 30.0
    client.close()
