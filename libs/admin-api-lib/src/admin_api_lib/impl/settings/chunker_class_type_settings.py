"""Settings for selecting the embedder implementation."""

from pydantic import Field
from pydantic_settings import BaseSettings

from admin_api_lib.impl.chunker.chunker_type import ChunkerType


class ChunkerClassTypeSettings(BaseSettings):
    """Settings controlling which chunker implementation is used."""

    class Config:
        """Configure environment integration for the settings."""

        env_prefix = "CHUNKER_CLASS_TYPE_"
        case_sensitive = False

    chunker_type: ChunkerType = Field(default=ChunkerType.RECURSIVE)
