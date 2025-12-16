"""Module that contains settings regarding the reranking."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class RerankerSettings(BaseSettings):
    """
    Contains settings regarding the reranking.

    Attributes
    ----------
    type : Literal["flashrank", "none"]
        Which reranker implementation to use (default "flashrank").
    k_documents : int
        The number of documents to return after reranking (default 5).
    min_relevance_score : float
        Minimum relevance threshold to return (default 0.001).
    enabled : bool
        A flag indicating whether the reranker is enabled (default True).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RERANKER_"
        case_sensitive = False

    type: Literal["flashrank", "none"] = Field(default="flashrank")
    k_documents: int = Field(default=5)
    min_relevance_score: float = Field(default=0.001)
    enabled: bool = Field(default=True)
