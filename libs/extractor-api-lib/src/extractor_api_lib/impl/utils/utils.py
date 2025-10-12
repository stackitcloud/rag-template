"""Module containing utility functions for the extractor API library."""

import datetime
import unicodedata
from hashlib import sha256


def hash_datetime() -> str:
    """
    Generate a SHA-256 hash of the current datetime.

    This function takes the current datetime, converts it to an ISO formatted string,
    encodes it to bytes, and then generates a SHA-256 hash of those bytes and returns
    a hexadecimal string representation of the hash.

    Returns
    -------
    str
        A hexadecimal string representing the SHA-256 hash of the current datetime.
    """
    now_bytes = datetime.datetime.now().isoformat().encode()
    return sha256(now_bytes).hexdigest()


def sanitize_file_name(name: str, *, strip_extension: bool = True) -> str:
    """
    Sanitize a file name consistently with ingestion and retrieval rules.

    - Transliterate German umlauts: ä->ae, ö->oe, ü->ue, ß->ss
    - Unicode normalize to NFKD and keep only ASCII alphanumeric and underscore
    - Optionally strip the extension (default True)

    Parameters
    ----------
    name : str
        Original file path or name.
    strip_extension : bool, optional
        If True, drop the trailing extension after the last dot (default True).

    Returns
    -------
    str
        The sanitized file name suitable for use in metadata filtering.
    """
    # Take only the last path segment if a path was provided
    base = name.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if strip_extension and "." in base:
        base = base[: base.rfind(".")]

    translit = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
    for ch, rep in translit.items():
        base = base.replace(ch, rep)

    # Normalize and keep only [A-Za-z0-9_]
    normalized = unicodedata.normalize("NFKD", base)
    sanitized = "".join(c for c in normalized if c.isalnum() or c == "_")
    return sanitized
