"""Module containing the ContentType enum."""

from enum import StrEnum, unique


@unique
class ContentType(StrEnum):
    """Enum describing the type of information extracted from a document."""

    TEXT = "TEXT"
    TABLE = "TABLE"
    SUMMARY = "SUMMARY"
    IMAGE = "IMAGE"
