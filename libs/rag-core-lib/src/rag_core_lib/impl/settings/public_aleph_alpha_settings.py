"""Module that contains settings regarding the alephalpha llm."""

from pydantic import Field
from pydantic_settings import BaseSettings


class PublicAlephAlphaSettings(BaseSettings):
    """Contains settings regarding alephalpha llm.

    Attributes
    ----------
    host : str
        The host URL for the Aleph Alpha API.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "PUBLIC_"
        case_sensitive = False

    host: str = Field(default="https://api.aleph-alpha.com")
