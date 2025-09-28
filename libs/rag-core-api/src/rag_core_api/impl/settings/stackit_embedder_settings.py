"""Module contains settings regarding the stackit embedder."""

from typing import Optional
from pydantic import Field, PositiveInt
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
    max_retries: Optional[PositiveInt]
        Total retries, not counting the initial attempt.
    retry_base_delay: Optional[float]
        Base delay in seconds for the first retry.
    retry_max_delay: Optional[float]
        Maximum delay cap in seconds for any single wait.
    backoff_factor: Optional[float]
        Exponential backoff factor (>= 1).
    attempt_cap: Optional[int]
        Cap for exponent growth (backoff_factor ** attempt_cap).
    jitter_min: Optional[float]
        Minimum jitter in seconds.
    jitter_max: Optional[float]
        Maximum jitter in seconds.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_EMBEDDER_"
        case_sensitive = False

    model: str = Field(default="intfloat/e5-mistral-7b-instruct")
    base_url: str = Field(default="https://e629124b-accc-4e25-a1cc-dc57ac741e1d.model-serving.eu01.onstackit.cloud/v1")
    api_key: str = Field(default="")
    max_retries: Optional[PositiveInt] = Field(
        default=None,
        title="Max Retries",
        description="Total retries, not counting the initial attempt.",
    )
    retry_base_delay: Optional[float] = Field(
        default=None,
        ge=0,
        title="Retry Base Delay",
        description="Base delay in seconds for the first retry.",
    )
    retry_max_delay: Optional[float] = Field(
        default=None,
        gt=0,
        title="Retry Max Delay",
        description="Maximum delay cap in seconds for any single wait.",
    )
    backoff_factor: Optional[float] = Field(
        default=None,
        ge=1.0,
        title="Backoff Factor",
        description="Exponential backoff factor (>= 1).",
    )
    attempt_cap: Optional[int] = Field(
        default=None,
        ge=0,
        title="Attempt Cap",
        description="Cap for exponent growth (backoff_factor ** attempt_cap).",
    )
    jitter_min: Optional[float] = Field(
        default=None,
        ge=0.0,
        title="Jitter Min (s)",
        description="Minimum jitter in seconds.",
    )
    jitter_max: Optional[float] = Field(
        default=None,
        ge=0.0,
        title="Jitter Max (s)",
        description="Maximum jitter in seconds.",
    )
