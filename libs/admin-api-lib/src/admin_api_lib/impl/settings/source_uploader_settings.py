"""Contains settings regarding the SourceUploader."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SourceUploaderSettings(BaseSettings):
    """
    Contains settings regarding the SourceUploader.

    Attributes
    ----------
    timeout : float
       The timeout for the SourceUploader.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "SOURCE_UPLOADER_"
        case_sensitive = False

    timeout: float = Field(default=3600.0, description="Timeout for the SourceUploader in seconds.")
