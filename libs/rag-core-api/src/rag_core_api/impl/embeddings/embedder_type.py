from enum import StrEnum, unique


@unique
class EmbedderType(StrEnum):
    ALEPHALPHA = "alephalpha"
    OLLAMA = "ollama"
    STACKIT = "stackit"
