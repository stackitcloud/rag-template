"""Contains settings for summarizer."""

from typing import Optional
from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SummarizerSettings(BaseSettings):
    """
    Contains settings regarding the summarizer.

    Attributes
    ----------
    maximum_input_size : int
        The maximum size of the input that the summarizer can handle. Default is 8000.
    maximum_concurrency : int
        The maximum number of concurrent summarization processes. Default is 10.
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

    model_config = SettingsConfigDict(env_prefix="SUMMARIZER_", case_sensitive=False)

    maximum_input_size: int = Field(default=8000)
    maximum_concurrency: int = Field(default=10)
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

    @model_validator(mode="after")
    def _check_relations(self) -> "SummarizerSettings":
        if not self.jitter_min or not self.jitter_max:
            return self
        if self.jitter_max < self.jitter_min:
            raise ValueError("jitter_max must be >= jitter_min")
        return self
