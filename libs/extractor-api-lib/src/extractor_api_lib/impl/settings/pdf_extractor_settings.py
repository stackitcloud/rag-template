"""Module for the settings of the S3 storage."""

from pydantic import Field
from pydantic_settings import BaseSettings


class PDFExtractorSettings(BaseSettings):
    """Contains settings regarding the S3 storage."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "pdf_extractor_"
        case_sensitive = False

    footer_height: int = Field(default=155)
    diagrams_folder_name: str = Field(
        default="connection_diagrams",
        description="Name of the folder where diagrams are stored.",
    )
