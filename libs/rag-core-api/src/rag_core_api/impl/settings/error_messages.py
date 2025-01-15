"""Module that contains settings regarding the error messages."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ErrorMessages(BaseSettings):
    """
    Contains settings regarding the error messages.

    Attributes
    ----------
    no_documents_message : str
        Default message when no documents are available.
    no_or_empty_collection : str
        Default message when no or empty collection of documents is provided.
    harmful_question : str
        Default message for harmful or inappropriate questions.
    no_answer_found : str
        Default message when no answer is found with the given context.
    empty_message : str
        Default message when an empty question is provided.
    """

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

    empty_message: str = Field(default="Es tut mir leid, ich kann keine leere Frage beantworten.")
