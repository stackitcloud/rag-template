"""Contains settings regarding langfuse."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RagasSettings(BaseSettings):
    """Contains settings regarding ragas."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "RAGAS_"
        case_sensitive = False

    is_debug: bool = Field(default=False)
    use_openai: bool = Field(default=True)
    model: str = Field(default="gpt-4o-mini")
    openai_api_key: str = Field(default="")
    timeout: int = Field(default=60)
    prompt_language: str = Field(default="german")
    evaluation_dataset_name: str = Field(default="eval-data")  # TODO: add config param in deployment
    dataset_filename: str = Field(default="test_data.json")
    max_concurrency: int = Field(default=5)
