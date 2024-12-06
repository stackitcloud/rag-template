"""Contains settings for summarizer."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SummarizerSettings(BaseSettings):
    """
    Contains settings regarding the summarizer.

    Attributes
    ----------
    maximum_input_size : int
        The maximum size of the input that the summarizer can handle. Default is 8000.
    maximum_concurrreny : int
        The maximum number of concurrent summarization processes. Default is 10.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "SUMMARIZER_"
        case_sensitive = False

    maximum_input_size: int = Field(default=8000)
    maximum_concurrreny: int = Field(default=10)
