"""Module contains settings for the retry decorator."""

from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetryDecoratorSettings(BaseSettings):
    """
    Contains settings regarding the retry decorator.

    Attributes
    ----------
    max_retries : int (> 0)
        Total retries (not counting the first attempt).
    retry_base_delay : float (>= 0)
        Base delay in seconds for the first retry.
    retry_max_delay : float (> 0)
        Maximum delay cap for any single wait.
    backoff_factor : float (>= 1)
        Exponential backoff factor.
    attempt_cap : int (>= 0)
        Cap for exponent growth (backoff_factor ** attempt_cap).
    jitter_min : float (>= 0)
        Minimum jitter to add to wait times.
    jitter_max : float (>= jitter_min)
        Maximum jitter to add to wait times.
    """

    model_config = SettingsConfigDict(env_prefix="RETRY_DECORATOR_", case_sensitive=False)

    max_retries: PositiveInt = Field(
        default=5,
        title="Max Retries",
        description="Total retries, not counting the initial attempt.",
    )
    retry_base_delay: float = Field(
        default=0.5,
        ge=0,
        title="Retry Base Delay",
        description="Base delay in seconds for the first retry.",
    )
    retry_max_delay: float = Field(
        default=600.0,
        gt=0,
        title="Retry Max Delay",
        description="Maximum delay cap in seconds for any single wait.",
    )
    backoff_factor: float = Field(
        default=2.0,
        ge=1.0,
        title="Backoff Factor",
        description="Exponential backoff factor (>= 1).",
    )
    attempt_cap: int = Field(
        default=6,
        ge=0,
        title="Attempt Cap",
        description="Cap for exponent growth (backoff_factor ** attempt_cap).",
    )
    jitter_min: float = Field(
        default=0.05,
        ge=0.0,
        title="Jitter Min (s)",
        description="Minimum jitter in seconds.",
    )
    jitter_max: float = Field(
        default=0.25,
        ge=0.0,
        title="Jitter Max (s)",
        description="Maximum jitter in seconds.",
    )

    @model_validator(mode="after")
    def _check_relations(self) -> "RetryDecoratorSettings":
        # Ensure jitter_max >= jitter_min
        if self.jitter_max < self.jitter_min:
            raise ValueError("jitter_max must be >= jitter_min")
        return self
