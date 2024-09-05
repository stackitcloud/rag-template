"""Contains the settings for the class types, if multiple classes can be selected"""

from pydantic import Field
from pydantic_settings import BaseSettings

from rag_core_api.impl.embeddings.embedder_type import EmbedderType


class EmbedderClassTypeSettings(BaseSettings):
    """
    Settings class for embedder class types.

    This class defines the configuration settings for embedder class types.
    It inherits from the BaseSettings class
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "EMBEDDER_CLASS_TYPE_"
        case_sensitive = False

    embedder_type: EmbedderType = Field(
        default=EmbedderType.MYAPI,
    )
