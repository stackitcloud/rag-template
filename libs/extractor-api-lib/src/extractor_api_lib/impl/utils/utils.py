"""Module containing utility functions for the extractor API library."""

import datetime
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
