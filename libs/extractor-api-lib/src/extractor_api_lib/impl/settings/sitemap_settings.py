"""Settings for sitemap extraction."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class SitemapSettings(BaseSettings):
    """Controls sitemap HTML parsing defaults."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "SITEMAP_"
        case_sensitive = False

    parser: Literal["docusaurus", "astro", "generic"] = Field(default="docusaurus")

