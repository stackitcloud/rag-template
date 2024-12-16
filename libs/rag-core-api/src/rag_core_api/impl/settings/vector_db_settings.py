"""Module that contains settings regarding the vector db."""

from pydantic_settings import BaseSettings


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

    collection_name: str
    url: str
