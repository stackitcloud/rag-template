"""Module that contains the settings for the class types, if multiple classes can be selected."""

from pydantic import Field
from pydantic_settings import BaseSettings

from rag_core_api.impl.embeddings.embedder_type import EmbedderType


class EmbedderClassTypeSettings(BaseSettings):
    """
    Settings class for embedder class types.

    Attributes
    ----------
    embedder_type : EmbedderType
        The type of embedder to be used (defaults EmbedderType.STACKIT).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "EMBEDDER_CLASS_TYPE_"
        case_sensitive = False

    embedder_type: EmbedderType = Field(
        default=EmbedderType.STACKIT,
    )
