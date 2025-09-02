import asyncio
import logging
import time
from typing import Optional

import pytest

from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.utils.retry_decorator import retry_with_backoff


class DummyError(Exception):
    pass


class RateLimitError(Exception):
    def __init__(self, headers: Optional[dict[str, str]] = None, status_code: Optional[int] = None):
        self.response = type("Resp", (), {"headers": headers or {}, "status_code": status_code})()
        super().__init__("rate limit")


@pytest.mark.asyncio
async def test_async_success_first_try():
    calls = {"n": 0}

    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2))
    async def fn():
        calls["n"] += 1
        return 42

    assert await fn() == 42
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_async_retries_then_success(monkeypatch):
    calls = {"n": 0}
    slept = []

    async def fake_sleep(x):
        slept.append(x)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=3, retry_base_delay=0.01))
    async def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise DummyError("boom")
        return "ok"

    assert await fn() == "ok"
    assert calls["n"] == 3
    # Expect at least two sleeps due to two failures
    assert len(slept) >= 2


def test_sync_success_first_try():
    calls = {"n": 0}

    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2))
    def fn():
        calls["n"] += 1
        return 7

    assert fn() == 7
    assert calls["n"] == 1


def test_sync_retries_then_fail(monkeypatch):
    calls = {"n": 0}
    slept = []

    def fake_sleep(x):
        slept.append(x)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2, retry_base_delay=0.01))
    def fn():
        calls["n"] += 1
        raise DummyError("always")

    with pytest.raises(DummyError):
        fn()
    # 1 initial + 2 retries = 3 calls total
    assert calls["n"] == 3
    # Two sleeps (after two failures)
    assert len(slept) == 2


@pytest.mark.asyncio
async def test_async_rate_limit_uses_header_wait(monkeypatch):
    calls = {"n": 0}
    slept = []

    async def fake_sleep(x):
        slept.append(x)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    headers = {
        "x-ratelimit-reset-requests": "1.5s",
        "x-ratelimit-remaining-requests": "0",
    }

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        rate_limit_exceptions=(RateLimitError,),
    )
    async def fn():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RateLimitError(headers=headers, status_code=429)
        return "ok"

    out = await fn()
    assert out == "ok"
    assert calls["n"] == 2
    # Should sleep roughly ~1.5s (+jitter). Verify >= 1.5
    assert any(x >= 1.5 for x in slept)


@pytest.mark.asyncio
async def test_is_rate_limited_callback(monkeypatch):
    calls = {"n": 0}
    slept = []

    async def fake_sleep(x):
        slept.append(x)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    def mark_rate_limited(exc: BaseException) -> bool:
        return isinstance(exc, DummyError)

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        is_rate_limited=mark_rate_limited,
    )
    async def fn():
        calls["n"] += 1
        if calls["n"] == 1:
            raise DummyError("treated as rate limited")
        return "ok"

    out = await fn()
    assert out == "ok"
    assert calls["n"] == 2
    assert len(slept) == 1


def test_sync_rate_limit_headers(monkeypatch):
    calls = {"n": 0}
    slept = []

    def fake_sleep(x):
        slept.append(x)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    headers = {
        "x-ratelimit-reset-requests": "2s",
    }

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        rate_limit_exceptions=(RateLimitError,),
    )
    def fn():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RateLimitError(headers=headers, status_code=429)
        return "ok"

    assert fn() == "ok"
    assert calls["n"] == 2
    assert any(x >= 2.0 for x in slept)
