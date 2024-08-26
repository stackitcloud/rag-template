"""Contains settings regarding the reranking."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RerankerSettings(BaseSettings):
    """Contains settings regarding the reranking."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RERANKER_"
        case_sensitive = False

    k_documents: int = Field(default=5)
