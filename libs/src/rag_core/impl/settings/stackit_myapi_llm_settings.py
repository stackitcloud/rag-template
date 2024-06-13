"""Contains settings regarding the stackit myapi llm."""

from pydantic import Field
from pydantic_settings import BaseSettings


class StackitMyAPILLMSettings(BaseSettings):
    """Contains settings regarding the stackit myapi llm."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_"
        case_sensitive = False

    auth_server_url: str = Field()
    auth_client_id: str = Field()
    auth_client_secret: str = Field()
    token_lifetime_margin: int = Field()  # in seconds
