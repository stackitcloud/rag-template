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
    model : str
        Flashrank model to use (default "ms-marco-TinyBERT-L-2-v2").
    min_relevance_score : float
        Minimum score threshold for keeping a document after reranking (default 0.0).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RERANKER_"
        case_sensitive = False

    type: Literal["flashrank", "none"] = Field(default="flashrank")
    k_documents: int = Field(default=5)
    model: str = Field(default="ms-marco-TinyBERT-L-2-v2")
    min_relevance_score: float = Field(default=0.0)
