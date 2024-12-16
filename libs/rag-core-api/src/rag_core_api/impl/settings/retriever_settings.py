"""Module that contains settings regarding the retriever."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RetrieverSettings(BaseSettings):
    """Contains settings regarding the retriever.

    threshold : float
        The threshold value for the retriever (default 0.5).
    k_documents : int
        The number of documents to retrieve (default 10).
    total_k : int
        The total number of documents (default 10).
    table_threshold : float
        The threshold value for table retrieval (default 0.37).
    table_k_documents : int
        The number of table documents to retrieve (default 10).
    summary_threshold : float
        The threshold value for summary retrieval (default 0.5).
    summary_k_documents : int
        The number of summary documents to retrieve (default 10).
    image_threshold : float
        The threshold value for image retrieval (default 0.5).
    image_k_documents : int
        The number of image documents to retrieve (default 10).
    """

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
