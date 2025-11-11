"""Generic text/language parsing utilities for rag-core-api.

These helpers are side-effect-free and safe to reuse across chains.
"""

from __future__ import annotations

import re
from typing import Any

# Compiled once at import time
LANG_LOCALE_RE = re.compile(r"^\s*([a-z]{2})(?:[-_][a-z]{2})?\s*$", re.IGNORECASE)
JSONISH_DQ_RE = re.compile(r'(?i)"language"\s*:\s*"([a-z]{2}(?:[-_][a-z]{2})?)"')
JSONISH_SQ_RE = re.compile(r"(?i)'language'\s*:\s*'([a-z]{2}(?:[-_][a-z]{2})?)'")
JSONISH_LOOSE_RE = re.compile(r"(?i)\blanguage\b\s*[:=]\s*\"?([a-z]{2}(?:[-_][a-z]{2})?)\"?")


def strip_code_fences(text: str) -> str:
    """Remove a single leading/trailing triple-backtick fence (any language tag)."""
    t = text.strip()
    if t.startswith("```") and t.endswith("```"):
        lines = t.splitlines()
        # drop first line if it's a fence
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        # drop last line if it's a fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return t


def norm_lang(code: str) -> str:
    """Return normalized 2-letter ISO 639-1 from 'xx' or 'xx-YY'/'xx_YY'; else ''."""
    if not isinstance(code, str):
        return ""
    code = code.strip().lstrip("\ufeff")  # handle BOM if present
    m = LANG_LOCALE_RE.match(code)
    return m.group(1).lower() if m else ""


def extract_lang_from_parsed(data: Any) -> str:
    """Try to extract language from already-parsed dict/list; return normalized code or ''."""
    if isinstance(data, dict) and "language" in data:
        return norm_lang(data.get("language", ""))
    if isinstance(data, list) and data and isinstance(data[0], dict) and "language" in data[0]:
        return norm_lang(data[0].get("language", ""))
    return ""
