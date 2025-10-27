"""Module containing the ChunkerType enumeration."""

from enum import StrEnum, unique


@unique
class ChunkerType(StrEnum):
    """An enumeration representing different types of chunkers."""

    SEMANTIC = "semantic"
    RECURSIVE = "recursive"
