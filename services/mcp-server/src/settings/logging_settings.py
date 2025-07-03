"""Contains settings regarding logging configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """
    Contains settings regarding logging configuration.

    Attributes
    ----------
    directory : str
        The directory path for the logging configuration file.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "LOGGING_"
        case_sensitive = False

    directory: str = Field(default="/config/logging.yaml")
