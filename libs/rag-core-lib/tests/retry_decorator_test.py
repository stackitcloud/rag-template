import asyncio
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


@pytest.fixture
def counter():
    class C:
        def __init__(self) -> None:
            self.n = 0

        def inc(self) -> int:
            self.n += 1
            return self.n

    return C()


@pytest.fixture
def async_sleeps(monkeypatch):
    sleeps: list[float] = []

    async def fake_sleep(x):
        sleeps.append(x)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    return sleeps


@pytest.fixture
def sync_sleeps(monkeypatch):
    sleeps: list[float] = []

    def fake_sleep(x):
        sleeps.append(x)

    monkeypatch.setattr(time, "sleep", fake_sleep)
    return sleeps


@pytest.mark.asyncio
async def test_async_success_first_try(counter):
    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2))
    async def fn():
        counter.inc()
        return 42

    assert await fn() == 42
    assert counter.n == 1


@pytest.mark.asyncio
async def test_async_retries_then_success(counter, async_sleeps):
    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=3, retry_base_delay=0.01))
    async def fn():
        if counter.inc() < 3:
            raise DummyError("boom")
        return "ok"

    assert await fn() == "ok"
    assert counter.n == 3
    assert len(async_sleeps) >= 2  # two failures -> two sleeps


def test_sync_success_first_try(counter):
    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2))
    def fn():
        counter.inc()
        return 7

    assert fn() == 7
    assert counter.n == 1


def test_sync_retries_then_fail(counter, sync_sleeps):
    @retry_with_backoff(settings=RetryDecoratorSettings(max_retries=2, retry_base_delay=0.01))
    def fn():
        counter.inc()
        raise DummyError("always")

    with pytest.raises(DummyError):
        fn()
    assert counter.n == 3  # 1 initial + 2 retries
    assert len(sync_sleeps) == 2


@pytest.mark.asyncio
async def test_async_rate_limit_uses_header_wait(counter, async_sleeps):
    headers = {"x-ratelimit-reset-requests": "1.5s", "x-ratelimit-remaining-requests": "0"}

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        rate_limit_exceptions=(RateLimitError,),
    )
    async def fn():
        if counter.inc() == 1:
            raise RateLimitError(headers=headers, status_code=429)
        return "ok"

    out = await fn()
    assert out == "ok"
    assert counter.n == 2
    assert any(x >= 1.5 for x in async_sleeps)


@pytest.mark.asyncio
async def test_is_rate_limited_callback(counter, async_sleeps):
    def mark_rate_limited(exc: BaseException) -> bool:  # noqa: ANN001 - explicit for clarity
        return isinstance(exc, DummyError)

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        is_rate_limited=mark_rate_limited,
    )
    async def fn():
        if counter.inc() == 1:
            raise DummyError("treated as rate limited")
        return "ok"

    out = await fn()
    assert out == "ok"
    assert counter.n == 2
    assert len(async_sleeps) == 1


def test_sync_rate_limit_headers(counter, sync_sleeps):
    headers = {"x-ratelimit-reset-requests": "2s"}

    @retry_with_backoff(
        settings=RetryDecoratorSettings(max_retries=1, retry_base_delay=0.01),
        rate_limit_exceptions=(RateLimitError,),
    )
    def fn():
        if counter.inc() == 1:
            raise RateLimitError(headers=headers, status_code=429)
        return "ok"

    assert fn() == "ok"
    assert counter.n == 2
    assert any(x >= 2.0 for x in sync_sleeps)
