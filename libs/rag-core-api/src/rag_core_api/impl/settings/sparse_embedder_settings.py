"""Module contains settings regarding the sparse embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SparseEmbedderSettings(BaseSettings):
    """
    Contains settings regarding the sparse embedder.

    Attributes
    ----------
    model_name : str
        The name of the model to be used (default "Qdrant/bm25").
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "SPARSE_EMBEDDER_"
        case_sensitive = False

    model_name: str = Field(default="Qdrant/bm25")
