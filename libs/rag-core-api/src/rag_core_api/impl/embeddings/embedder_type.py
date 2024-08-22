from enum import StrEnum, unique


@unique
class EmbedderType(StrEnum):
    MYAPI = "myapi"
    ALEPHALPHA = "alephalpha"
    OLLAMA = "ollama"
