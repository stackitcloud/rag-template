"""Reusable exponential backoff / retry decorator for sync and async functions."""

import asyncio
import inspect
import logging
import random
import time
from functools import wraps
from typing import Callable, Optional, ParamSpec, TypeVar

from pydantic_settings import BaseSettings

from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.utils.utils import (
    headers_from_exception,
    status_code_from_exception,
    wait_from_rate_limit_headers,
)


# Use ParamSpec and TypeVar for type-safe decorators
P = ParamSpec("P")
R = TypeVar("R")


class _RetryEngine:
    """Internal helper to keep retry logic small in the public API function."""

    def __init__(
        self,
        cfg: RetryDecoratorSettings,
        exceptions: tuple[type[BaseException], ...],
        rate_limit_exceptions: tuple[type[BaseException], ...],
        rate_limit_statuses: tuple[int, ...],
        rate_limit_header_names: tuple[str, ...],
        is_rate_limited: Optional[Callable[[BaseException], bool]],
        logger: Optional[logging.Logger],
    ) -> None:
        self.cfg = cfg
        self.exceptions = exceptions
        self.rate_limit_exceptions = rate_limit_exceptions
        self.rate_limit_statuses = rate_limit_statuses
        self.rate_limit_header_names = rate_limit_header_names
        self.is_rate_limited_cb = is_rate_limited
        self.logger = logger

    def decorate(self, fn: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(fn):
            return self._decorate_async(fn)
        return self._decorate_sync(fn)

    def _decorate_async(self, fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(self.cfg.max_retries + 1):
                try:
                    return await fn(*args, **kwargs)
                except self.exceptions as exc:  # type: ignore[misc]
                    wait_time = self._calculate_wait_time(attempt, exc)
                    if wait_time is None:
                        raise
                    await asyncio.sleep(wait_time)
            raise AssertionError("Retry loop exited unexpectedly.")

        return async_wrapper

    def _decorate_sync(self, fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(self.cfg.max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except self.exceptions as exc:  # type: ignore[misc]
                    wait_time = self._calculate_wait_time(attempt, exc)
                    if wait_time is None:
                        raise
                    time.sleep(wait_time)
            raise AssertionError("Retry loop exited unexpectedly.")

        return sync_wrapper

    def _should_rate_limited(self, exc: BaseException) -> bool:
        if self.is_rate_limited_cb and self.is_rate_limited_cb(exc):
            return True
        if isinstance(exc, self.rate_limit_exceptions):
            return True
        status_code = status_code_from_exception(exc)
        if status_code in self.rate_limit_statuses:
            return True
        msg = str(exc).lower()
        return ("rate limit" in msg) or ("ratelimit" in msg)

    def _compute_backoff_wait(self, attempt: int) -> float:
        delay = self.cfg.retry_base_delay * (self.cfg.backoff_factor ** min(attempt, self.cfg.attempt_cap))
        return min(delay, self.cfg.retry_max_delay)

    def _with_jitter(self, seconds: float) -> float:
        return min(
            seconds + random.uniform(self.cfg.jitter_min, self.cfg.jitter_max),  # noqa: S311 non-crypto jitter
            self.cfg.retry_max_delay,
        )

    def _calculate_wait_time(self, attempt: int, exc: BaseException) -> Optional[float]:
        """Return wait seconds or None to re-raise."""
        total_attempts = self.cfg.max_retries + 1
        if attempt == self.cfg.max_retries:
            if self.logger:
                self.logger.error("Failed after %d attempts: %s", total_attempts, exc, exc_info=False)
            return None

        if self._should_rate_limited(exc):
            headers = headers_from_exception(exc)
            wait = wait_from_rate_limit_headers(headers, self.rate_limit_header_names)
            if wait is None:
                wait = self._compute_backoff_wait(attempt)
            final_wait = self._with_jitter(wait)
            if self.logger:
                self.logger.warning(
                    (
                        "Rate limited. Remaining: req=%s tok=%s. Reset in: req=%s tok=%s. "
                        "Retrying in %.2fs (attempt %d/%d)..."
                    ),
                    headers.get("x-ratelimit-remaining-requests", "?"),
                    headers.get("x-ratelimit-remaining-tokens", "?"),
                    headers.get("x-ratelimit-reset-requests", "?"),
                    headers.get("x-ratelimit-reset-tokens", "?"),
                    final_wait,
                    attempt + 1,
                    total_attempts,
                )
            return final_wait

        delay = self._compute_backoff_wait(attempt)
        if self.logger:
            self.logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %.2fs...",
                attempt + 1,
                total_attempts,
                exc,
                delay,
                exc_info=False,
            )
        return delay


def retry_with_backoff(
    *,
    settings: RetryDecoratorSettings | None = None,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    rate_limit_exceptions: tuple[type[BaseException], ...] = (),
    rate_limit_statuses: tuple[int, ...] = (429,),
    rate_limit_header_names: tuple[str, ...] = (
        "x-ratelimit-reset-requests",
        "x-ratelimit-reset-tokens",
    ),
    is_rate_limited: Optional[Callable[[BaseException], bool]] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Apply robust retry logic with exponential backoff and rate-limit awareness."""
    cfg = settings or RetryDecoratorSettings()
    engine = _RetryEngine(
        cfg=cfg,
        exceptions=exceptions,
        rate_limit_exceptions=rate_limit_exceptions,
        rate_limit_statuses=rate_limit_statuses,
        rate_limit_header_names=rate_limit_header_names,
        is_rate_limited=is_rate_limited,
        logger=logger,
    )
    return engine.decorate


def create_retry_decorator_settings(
    ai_settings: BaseSettings, retry_decorator_settings: RetryDecoratorSettings
) -> RetryDecoratorSettings:
    """Create retry decorator settings based on AI and default settings.

    If the corresponding field in ai_settings is not set, the value from retry_decorator_settings will be used.

    Parameters
    ----------
    ai_settings : BaseSettings
        Those are the AI settings, e.g. Embeddings, Summarizers etc.
    retry_decorator_settings : RetryDecoratorSettings
        Those are the default retry settings.

    Returns
    -------
    RetryDecoratorSettings
        The combined retry settings.
    """
    fields = [
        "max_retries",
        "retry_base_delay",
        "retry_max_delay",
        "backoff_factor",
        "attempt_cap",
        "jitter_min",
        "jitter_max",
    ]
    settings_kwargs = {
        field: (
            getattr(ai_settings, field)
            if getattr(ai_settings, field) is not None
            else getattr(retry_decorator_settings, field)
        )
        for field in fields
    }
    if settings_kwargs["jitter_max"] < settings_kwargs["jitter_min"]:
        raise ValueError("jitter_max must be >= jitter_min")
    return RetryDecoratorSettings(**settings_kwargs)
