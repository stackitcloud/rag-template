"""Contains settings regarding langfuse."""

from pydantic_settings import BaseSettings
from pydantic import Field


class LangfuseSettings(BaseSettings):
    """Contains settings regarding langfuse."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "LANGFUSE_"
        case_sensitive = False

    secret_key: str = Field()
    public_key: str = Field()
    host: str = Field()
    dataset_filename: str = Field(default="test_data.json")
