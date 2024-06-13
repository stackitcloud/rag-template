"""Contains settings regarding the aleph_alpha embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ErrorMessages(BaseSettings):
    """Contains settings regarding the aleph_alpha embedder."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "ERROR_MESSAGES_"
        case_sensitive = False

    no_documents_message: str = Field(
        default="Es tut mir leid, meine Antworten sind begrenzt. Sie müssen die richtigen Fragen stellen."
    )
    no_or_empty_collection: str = Field(
        default="Es tut mir leid, aber es wurden keine Dokumente bereitgestellt, welche ich durchsuchen könnte."
    )
    no_product_name_message: str = Field(
        default="""Es wurde kein Produktname im chat-verlauf gefunden.
        Ich habe derzeit Informationen über folgende Produkte:"""
    )
