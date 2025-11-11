"""Contains settings regarding the chunker."""

from pydantic import Field
from pydantic_settings import BaseSettings


class DocumentExtractorSettings(BaseSettings):
    """Contains settings regarding the document extractor microservice.

    Attributes
    ----------
    host (str): The url to the api.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "DOCUMENT_EXTRACTOR_"
        case_sensitive = False

    host: str = Field(default="http://extractor:8080")
