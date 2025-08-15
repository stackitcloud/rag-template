"""Reusable exponential backoff / retry decorator for sync and async functions."""

import asyncio
import inspect
import logging
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, ParamSpec, Tuple, Type, TypeVar

from rag_core_lib.impl.utils.utils import headers_from_exception, status_code_from_exception, wait_from_rate_limit_headers


@dataclass
class RetrySettings:
    max_retries: int = 5          # total retries (not counting the first attempt)
    retry_base_delay: float = 0.5   # seconds
    retry_max_delay: float = 600.0   # cap for any single wait
    backoff_factor: float = 2.0     # exponential factor
    attempt_cap: int = 6            # cap exponent growth (2**attempt_cap)
    jitter_min: float = 0.05        # seconds
    jitter_max: float = 0.25        # seconds


# Use ParamSpec and TypeVar for type-safe decorators
P = ParamSpec("P")
R = TypeVar("R")


def retry_with_backoff(
    *,
    settings: RetrySettings | None = None,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    rate_limit_exceptions: Tuple[Type[BaseException], ...] = (),
    rate_limit_statuses: Tuple[int, ...] = (429,),
    rate_limit_header_names: Tuple[str, ...] = ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"),
    is_rate_limited: Optional[Callable[[BaseException], bool]] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Apply robust retry logic with exponential backoff and optional rate-limit awareness.
    """
    cfg = settings or RetrySettings()

    def _should_treat_as_rate_limited(exc: BaseException) -> bool:
        if is_rate_limited and is_rate_limited(exc):
            return True
        if isinstance(exc, rate_limit_exceptions):
            return True
        status_code = status_code_from_exception(exc)
        if status_code in rate_limit_statuses:
            return True
        msg = str(exc).lower()
        return ("rate limit" in msg) or ("ratelimit" in msg)

    def _compute_backoff_wait(attempt: int) -> float:
        delay = cfg.retry_base_delay * (cfg.backoff_factor ** min(attempt, cfg.attempt_cap))
        return min(delay, cfg.retry_max_delay)

    def _with_jitter(seconds: float) -> float:
        return min(seconds + random.uniform(cfg.jitter_min, cfg.jitter_max), cfg.retry_max_delay)

    def _calculate_wait_time(attempt: int, exc: BaseException) -> float | None:
        """
        Centralizes the logic for calculating wait time.
        Returns None if the exception should be re-raised immediately.
        """
        total_attempts = cfg.max_retries + 1
        if attempt == cfg.max_retries:
            if logger:
                logger.error("Failed after %d attempts: %s", total_attempts, exc, exc_info=False)
            return None  # Signal to re-raise

        if _should_treat_as_rate_limited(exc):
            headers = headers_from_exception(exc)
            wait = wait_from_rate_limit_headers(headers, rate_limit_header_names)
            if wait is None:
                wait = _compute_backoff_wait(attempt)

            final_wait = _with_jitter(wait)
            if logger:
                logger.warning(
                    "Rate limited. Remaining: req=%s tok=%s. Reset in: req=%s tok=%s. Retrying in %.2fs (attempt %d/%d)...",
                    headers.get("x-ratelimit-remaining-requests", "?"),
                    headers.get("x-ratelimit-remaining-tokens", "?"),
                    headers.get("x-ratelimit-reset-requests", "?"),
                    headers.get("x-ratelimit-reset-tokens", "?"),
                    final_wait,
                    attempt + 1,
                    total_attempts,
                )
                logger.warning("headers: %s", headers)
            return final_wait
        else:
            delay = _compute_backoff_wait(attempt)
            if logger:
                logger.warning(
                    "Attempt %d/%d failed: %s. Retrying in %.2fs...",
                    attempt + 1,
                    total_attempts,
                    exc,
                    delay,
                    exc_info=False,
                )
            return delay

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                for attempt in range(cfg.max_retries + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions as exc:  # type: ignore[misc]
                        wait_time = _calculate_wait_time(attempt, exc)
                        if wait_time is None:
                            raise
                        await asyncio.sleep(wait_time)
                # This line should be unreachable if max_retries >= 0
                raise AssertionError("Retry loop exited unexpectedly.")
            return async_wrapper
        else:
            @wraps(fn)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                for attempt in range(cfg.max_retries + 1):
                    try:
                        return fn(*args, **kwargs)
                    except exceptions as exc:  # type: ignore[misc]
                        wait_time = _calculate_wait_time(attempt, exc)
                        if wait_time is None:
                            raise
                        time.sleep(wait_time)
                # This line should be unreachable if max_retries >= 0
                raise AssertionError("Retry loop exited unexpectedly.")
            return sync_wrapper

    return decorator
