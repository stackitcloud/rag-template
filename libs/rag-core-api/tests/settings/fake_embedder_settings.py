"""Module contains settings regarding the fake embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class FakeEmbedderSettings(BaseSettings):
    """
    Contains settings regarding the fake embedder.

    Attributes
    ----------
    size : int
        The size parameter for the embedder (default 386).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "FAKE_EMBEDDER_"
        case_sensitive = False

    size: int = Field(default=386)
