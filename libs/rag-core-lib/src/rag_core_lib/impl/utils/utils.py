"""Module for utility functions."""

import re
from typing import Any, Iterable, Optional


def _to_seconds(v):
    if v is None:
        return None
    try:
        s = str(v).strip().lower()
        # Support composite durations like "1h21m55s", as well as single-unit values
        if any(u in s for u in ("h", "m", "s")):
            total = 0.0
            for val, unit in re.findall(r"([0-9]+(?:\.[0-9]+)?)([hms])", s):
                num = float(val)
                if unit == "h":
                    total += num * 3600
                elif unit == "m":
                    total += num * 60
                else:  # "s"
                    total += num
            return total
        # Fallback: plain number interpreted as seconds
        return float(s)
    except Exception:
        return None


def _normalize_dict_items(items: Iterable[Any]) -> dict[str, str]:
    """Normalize dict items by converting keys and values to a consistent format."""
    return {str(k).lower(): str(v).lower() for k, v in items if k is not None and v is not None}


def _normalize_headers(raw_headers: Any) -> dict[str, str]:
    """Return a lowercased dict[str, str] from httpx.Headers or mapping-like objects."""
    if not raw_headers:
        return {}
    try:
        if hasattr(raw_headers, "items"):
            items = list(raw_headers.items())  # works for dict-like and httpx.Headers
        else:
            items = list(dict(raw_headers).items())
    except Exception:
        try:
            items = list(dict(raw_headers).items())
        except Exception:
            items = []

    return _normalize_dict_items(items)


def status_code_from_exception(exc: BaseException) -> Optional[int]:
    """Extract the HTTP status code from an exception, if available.

    Parameters
    ----------
    exc : BaseException
        The exception from which to extract the status code.

    Returns
    -------
    Optional[int]
        The HTTP status code if available, otherwise None.
    """
    resp = getattr(exc, "response", None)
    return getattr(resp, "status_code", None)


def headers_from_exception(exc: BaseException) -> dict[str, str]:
    """Extract HTTP headers from an exception, if available.

    Parameters
    ----------
    exc : BaseException
        The exception from which to extract the headers.

    Returns
    -------
    dict[str, str]
        The HTTP headers if available, otherwise an empty dictionary.
    """
    resp = getattr(exc, "response", None)
    raw = getattr(resp, "headers", None)
    return _normalize_headers(raw)


def wait_from_rate_limit_headers(
    headers: dict[str, str],
    header_names: Iterable[str] = ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"),
) -> Optional[float]:
    """Extract the wait time from rate limit headers, if available.

    Parameters
    ----------
    headers : dict[str, str]
        The HTTP headers from which to extract the wait time.
    header_names : Iterable[str], optional
        The header names to look for, by default ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens")

    Returns
    -------
    Optional[float]
        The wait time in seconds if available, otherwise None.
    """
    candidates = []
    for name in header_names:
        sec = _to_seconds(headers.get(name))
        if sec is not None:
            candidates.append(sec)
    return max(candidates) if candidates else None
