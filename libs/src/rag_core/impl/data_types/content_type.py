"""Enum describing the type of information extracted from a document."""

from enum import StrEnum, unique


@unique
class ContentType(StrEnum):
    """Enum describing the type of information extracted from a document."""

    TEXT = "text"
    TABLE = "table"
    SUMMARY = "summary"
    IMAGE = "image"
