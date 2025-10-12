"""Module for utilities."""

import unicodedata

TRANSLITERATION_MAP = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "ß": "ss",
}


def sanitize_document_name(document_name: str) -> str:
    """Sanitize a document name.

    replaces characters based on a transliteration map and normalizes the string to contain
    only alphanumeric characters, underscores, and periods.

    Parameters
    ----------
    document_name : str
        The original document name to be sanitized.

    Returns
    -------
    str
        The sanitized document name.
    """
    for char, replacement in TRANSLITERATION_MAP.items():
        document_name = document_name.replace(char, replacement)
    document_name = "".join(e for e in unicodedata.normalize("NFKD", document_name) if e.isalnum() or e in {"_", "."})
    return document_name


def sanitize_file_stem(file_name: str) -> str:
    """Return a sanitized filename without its extension.

    Applies the same normalization as sanitize_document_name and then strips
    the last extension (after the final dot). If no dot is present, returns
    the sanitized string as-is.
    """
    sanitized = sanitize_document_name(file_name)
    base = sanitized.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if "." in base:
        return base[: base.rfind(".")]
    return base
