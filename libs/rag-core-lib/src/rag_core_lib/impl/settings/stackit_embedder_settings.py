"""Settings regarding the STACKIT embedder."""

from typing import Optional

from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StackitEmbedderSettings(BaseSettings):
    """Configuration for the STACKIT embeddings endpoint."""

    model_config = SettingsConfigDict(env_prefix="STACKIT_EMBEDDER_", case_sensitive=False)

    model: str = Field(default="intfloat/e5-mistral-7b-instruct")
    base_url: str = Field(
        default="https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1",
    )
    api_key: str = Field(default="")
    max_retries: Optional[PositiveInt] = Field(default=None)
    retry_base_delay: Optional[float] = Field(default=None, ge=0)
    retry_max_delay: Optional[float] = Field(default=None, gt=0)
    backoff_factor: Optional[float] = Field(default=None, ge=1.0)
    attempt_cap: Optional[int] = Field(default=None, ge=0)
    jitter_min: Optional[float] = Field(default=None, ge=0.0)
    jitter_max: Optional[float] = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def _check_relations(self) -> "StackitEmbedderSettings":
        """Ensure that retry-related ranges are valid."""

        if not self.jitter_min or not self.jitter_max:
            return self
        if self.jitter_max < self.jitter_min:
            msg = "jitter_max must be >= jitter_min"
            raise ValueError(msg)
        return self
