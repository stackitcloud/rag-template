"""Settings regarding the Ollama embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaEmbedderSettings(BaseSettings):
    """Configuration for a local Ollama embeddings model."""

    class Config:
        """Configure environment integration for the settings."""

        env_prefix = "OLLAMA_EMBEDDER_"
        case_sensitive = False

    model: str = Field(default="bge-m3")
    base_url: str = Field(default="http://ollama:11434")
