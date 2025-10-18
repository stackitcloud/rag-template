"""Settings for selecting the embedder implementation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from rag_core_lib.impl.embeddings.embedder_type import EmbedderType


class EmbedderClassTypeSettings(BaseSettings):
    """Settings controlling which embedder implementation is used."""

    class Config:
        """Configure environment integration for the settings."""

        env_prefix = "EMBEDDER_CLASS_TYPE_"
        case_sensitive = False

    embedder_type: EmbedderType = Field(default=EmbedderType.STACKIT)
