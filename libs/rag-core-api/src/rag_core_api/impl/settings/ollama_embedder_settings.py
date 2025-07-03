"""Module contains settings regarding the Ollama embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaEmbedderSettings(BaseSettings):
    """
    Contains settings regarding the Ollama embedder.

    Attributes
    ----------
    model : str
        The model to be used (default "bge-m3").
    base_url : str
        The base URL for the Ollama server (default "http://ollama:11434").
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "OLLAMA_EMBEDDER_"
        case_sensitive = False

    model: str = Field(default="bge-m3")
    base_url: str = Field(default="http://ollama:11434")
