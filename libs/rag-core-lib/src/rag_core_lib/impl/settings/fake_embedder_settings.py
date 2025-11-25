"""Settings for the deterministic fake embedder used in tests."""

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class FakeEmbedderSettings(BaseSettings):
    """Configuration for the fake embedder implementation."""

    class Config:
        """Configure environment integration for the settings."""

        env_prefix = "FAKE_EMBEDDER_"
        case_sensitive = False

    size: PositiveInt = Field(default=768)
