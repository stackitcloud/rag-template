"""Module that contains settings for the Fake LLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class BackendSettings(BaseSettings):
    """
    Settings for the connection to the backend.

    Attributes
    ----------
    base_path : str
        The base path to the rag backend.
    """

    class Config:
        """Configuration for reading fields from the environment."""

        env_prefix = "BACKEND_"
        case_sensitive = False

    base_path: str = Field(default="http://127.0.0.1:8080")
