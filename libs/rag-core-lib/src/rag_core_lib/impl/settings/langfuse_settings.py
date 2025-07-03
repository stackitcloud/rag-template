"""Contains settings regarding Langfuse."""

from pydantic import Field
from pydantic_settings import BaseSettings


class LangfuseSettings(BaseSettings):
    """
    Contains settings regarding Langfuse.

    Attributes
    ----------
    secret_key : str
        The secret key for Langfuse.
    public_key : str
        The public key for Langfuse.
    host : str
        The host for Langfuse.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "LANGFUSE_"
        case_sensitive = False

    secret_key: str = Field()
    public_key: str = Field()
    host: str = Field()
