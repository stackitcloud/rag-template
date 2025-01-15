"""Module containing the EmbedderType enumeration."""

from enum import StrEnum, unique


@unique
class EmbedderType(StrEnum):
    """An enumeration representing different types of embedders."""

    OLLAMA = "ollama"
    STACKIT = "stackit"
    FAKE = "fake"
