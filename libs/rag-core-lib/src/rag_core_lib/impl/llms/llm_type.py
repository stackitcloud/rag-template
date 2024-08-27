from enum import StrEnum, unique


@unique
class LLMType(StrEnum):
    MYAPI = "myapi"
    ALEPHALPHA = "alephalpha"
    OLLAMA = "ollama"
    STACKIT = "stackit"
