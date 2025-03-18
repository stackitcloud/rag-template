"""Module that contains settings regarding the vector db."""

from pydantic_settings import BaseSettings
from pydantic import Field

from langchain_qdrant import RetrievalMode


class VectorDatabaseSettings(BaseSettings):
    """
    Contains settings regarding the vector db.

    Attributes
    ----------
    collection_name : str
        The name of the collection.
    url : str
        The URL of the vector database.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "VECTOR_DB_"
        case_sensitive = False

    collection_name: str = Field()
    location: str = Field()
    validate_collection_config: bool = Field(
        default=False
    )  # if true and collection does not exist, an error will be raised
    retrieval_mode: RetrievalMode = Field(default=RetrievalMode.HYBRID)
