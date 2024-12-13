"""Contains settings regarding the stackit embedder."""

from pydantic import Field
from pydantic_settings import BaseSettings


class StackitEmbedderSettings(BaseSettings):
    """Contains settings regarding the stackit embedder."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_EMBEDDER_"
        case_sensitive = False

    model: str = Field(default="intfloat/e5-mistral-7b-instruct")
    base_url: str = Field(default="https://e629124b-accc-4e25-a1cc-dc57ac741e1d.model-serving.eu01.onstackit.cloud/v1")
    api_key: str = Field()
