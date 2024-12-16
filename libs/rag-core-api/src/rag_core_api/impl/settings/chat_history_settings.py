"""Module that contains the settings of the chat history."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ChatHistorySettings(BaseSettings):
    """Contains settings regarding the chat history.

    Attributes
    ----------
    limit : int
        The maximum number of chat history entries to retrieve (default 4).
    reverse : bool
        Whether to reverse the order of the chat history (default True).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CHAT_HISTORY_"
        case_sensitive = False

    limit: int = Field(default=4)
    reverse: bool = Field(default=True)
