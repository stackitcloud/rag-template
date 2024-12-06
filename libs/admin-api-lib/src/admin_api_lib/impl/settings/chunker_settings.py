"""Contains settings regarding the chunker."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ChunkerSettings(BaseSettings):
    """Contains settings regarding the chunker.

    Attributes
    ----------
    max_size (int): The maximum size of the chunks.
    overlap (int): The overlap between the chunks.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CHUNKER_"
        case_sensitive = False

    max_size: int = Field(default=1000)
    overlap: int = Field(default=100)
