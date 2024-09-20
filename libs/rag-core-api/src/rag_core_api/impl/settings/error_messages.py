"""Contains settings regarding the error messages."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ErrorMessages(BaseSettings):
    """Contains settings regarding the error messages."""

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

    harmful_question: str = Field(
        default="Es tut mir leid, aber auf schädliche Anfragen kann nicht eingegangen werden."
    )

    no_answer_found: str = Field(
        default="Es tut mir leid, mit dem mir bereitgestellten Kontext konnte ich keine Antwort finden."
    )
