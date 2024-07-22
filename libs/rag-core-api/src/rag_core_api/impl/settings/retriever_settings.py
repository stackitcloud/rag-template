"""Contains settings regarding the retriever."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RetrieverSettings(BaseSettings):
    """Contains settings regarding the retriever."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RETRIEVER_"
        case_sensitive = False

    threshold: float = Field(default=0.5)
    k_documents: int = Field(default=10)
    total_k: int = Field(default=10)
    table_threshold: float = Field(default=0.37)
    table_k_documents: int = Field(default=10)
    summary_threshold: float = Field(default=0.5)
    summary_k_documents: int = Field(default=10)
    image_threshold: float = Field(default=0.5)
    image_k_documents: int = Field(default=10)
