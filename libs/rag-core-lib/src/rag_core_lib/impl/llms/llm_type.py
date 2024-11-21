from enum import StrEnum, unique


@unique
class LLMType(StrEnum):
    ALEPHALPHA = "alephalpha"
    OLLAMA = "ollama"
    STACKIT = "stackit"
