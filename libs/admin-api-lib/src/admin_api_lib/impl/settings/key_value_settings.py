"""Contains settings regarding the key values store."""

from pydantic import Field
from pydantic_settings import BaseSettings


class KeyValueSettings(BaseSettings):
    """
    Contains settings regarding the key value store.

    Attributes
    ----------
    host : str
        The hostname of the key value store.
    port : int
        The port number of the key value store.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "USECASE_KEYVALUE_"
        case_sensitive = False

    host: str = Field()
    port: int = Field()
