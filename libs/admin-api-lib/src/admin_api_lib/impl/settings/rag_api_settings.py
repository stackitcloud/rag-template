"""Contains settings regarding the chunker."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RAGAPISettings(BaseSettings):
    """Contains settings regarding the rag api microservice.

    Attributes
    ----------
    host (str): The url to the api.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RAG_API"
        case_sensitive = False

    host: str = Field(default="http://backend:8080")
