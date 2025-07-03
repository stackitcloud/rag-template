"""Contains settings regarding the S3 storage."""

from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    """
    Contains settings regarding the S3 storage.

    Attributes
    ----------
    secret_access_key : str
        The secret access key for S3.
    access_key_id : str
        The access key ID for S3.
    endpoint : str
        The endpoint URL for S3.
    bucket : str
        The bucket name in S3.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "S3_"
        case_sensitive = False

    secret_access_key: str
    access_key_id: str
    endpoint: str
    bucket: str
