"""Contains settings for summarizer."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SummarizerSettings(BaseSettings):
    """Contains settings regarding the summarizer."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "SUMMARIZER_"
        case_sensitive = False

    maximum_input_size: int = Field(default=8000)
    maximum_concurrreny: int = Field(default=10)
