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
