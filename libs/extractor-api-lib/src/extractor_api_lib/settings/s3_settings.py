"""Module for the settings of the S3 storage."""

from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    """Contains settings regarding the S3 storage."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "S3_"
        case_sensitive = False

    secret_access_key: str
    access_key_id: str
    endpoint: str
    bucket: str
