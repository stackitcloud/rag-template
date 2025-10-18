"""Contains settings regarding the chunker."""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class ChunkerSettings(BaseSettings):
    """Contains settings regarding the chunker configuration."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CHUNKER_"
        case_sensitive = False

    mode: Literal["recursive", "semantic"] = Field(default="recursive")
    max_size: int = Field(default=1000, gt=0)
    overlap: int = Field(default=100, ge=0)

    semantic_breakpoint_threshold_type: Literal[
        "percentile",
        "standard_deviation",
        "interquartile",
    ] = Field(default="percentile")
    semantic_breakpoint_threshold: float = Field(default=95.0, ge=0.0)
    semantic_buffer_size: int = Field(default=1, ge=0)
    semantic_min_chunk_size: int = Field(default=200, gt=0)
    semantic_max_chunk_size: int | None = Field(default=1200, gt=0)
    semantic_trim_chunks: bool = Field(default=True)

    @model_validator(mode="after")
    def _validate_min_max(self) -> "ChunkerSettings":
        if self.mode != "semantic":
            return self
        if (
            self.semantic_max_chunk_size is not None
            and self.semantic_min_chunk_size > self.semantic_max_chunk_size
        ):
            msg = "semantic_min_chunk_size cannot exceed semantic_max_chunk_size"
            raise ValueError(msg)
        return self
