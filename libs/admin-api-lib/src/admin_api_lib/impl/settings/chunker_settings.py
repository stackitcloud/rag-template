"""Contains settings regarding the chunker."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class ChunkerSettings(BaseSettings):
    """Contains settings regarding the chunker configuration."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "CHUNKER_"
        case_sensitive = False

    max_size: int = Field(default=1000, gt=0)
    overlap: int = Field(default=100, ge=0)

    breakpoint_threshold_type: Literal[
        "percentile",
        "standard_deviation",
        "interquartile",
        "gradient",
    ] = Field(default="percentile")
    breakpoint_threshold_amount: float = Field(default=95.0, ge=0.0)
    buffer_size: int = Field(default=1, ge=0)
    min_size: int = Field(default=200, gt=0)
