"""Module that contains the settings for the class types, if multiple classes can be selected."""

from pydantic import Field
from pydantic_settings import BaseSettings

from rag_core_lib.impl.llms.llm_type import LLMType


class RAGClassTypeSettings(BaseSettings):
    """
    Settings class for RAG class types.

    This class defines the configuration settings for RAG class types.
    It inherits from the BaseSettings class.

    Attributes
    ----------
    llm_type : LLMType
        The type of language model to use.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RAG_CLASS_TYPE_"
        case_sensitive = False

    llm_type: LLMType = Field(
        default=LLMType.STACKIT,
    )
