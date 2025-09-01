"""Module contains settings regarding the stackit embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class StackitEmbedderSettings(BaseSettings):
    """
    Contains settings regarding the stackit embedder.

    Attributes
    ----------
    model : str
        The model to be used (default "intfloat/e5-mistral-7b-instruct").
    base_url : str
        The base URL for the model serving
        (default "https://e629124b-accc-4e25-a1cc-dc57ac741e1d.model-serving.eu01.onstackit.cloud/v1").
    api_key : str
        The API key for authentication.
    max_retries : int
        Maximum number of retry attempts (default 10).
    retry_base_delay : float
        Base delay in seconds for exponential backoff (default 1.0).
    retry_max_delay : float
        Maximum delay in seconds between retries (default 60.0).
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_EMBEDDER_"
        case_sensitive = False

    model: str = Field(default="intfloat/e5-mistral-7b-instruct")
    base_url: str = Field(default="https://e629124b-accc-4e25-a1cc-dc57ac741e1d.model-serving.eu01.onstackit.cloud/v1")
    api_key: str = Field(default="")
    max_retries: int = Field(default=10, description="Maximum number of retry attempts")
    retry_base_delay: float = Field(default=1.0, description="Base delay in seconds for exponential backoff")
    retry_max_delay: float = Field(default=600.0, description="Maximum delay in seconds between retries")
