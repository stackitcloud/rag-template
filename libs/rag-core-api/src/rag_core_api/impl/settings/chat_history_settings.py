"""Contains settings regarding the chat history."""

# TODO add to infrastructure repo!
from pydantic import Field
from pydantic_settings import BaseSettings


class ChatHistorySettings(BaseSettings):
    """Contains settings regarding the chat history."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CHAT_HISTORY_"
        case_sensitive = False

    limit: int = Field(default=4)
    reverse: bool = Field(default=True)
