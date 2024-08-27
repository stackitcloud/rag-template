"""Contains settings regarding the stackit vllm."""

from pydantic_settings import BaseSettings
from pydantic import Field


class StackitVllmSettings(BaseSettings):
    """Contains settings regarding the stackit vllm."""

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_VLLM_"
        case_sensitive = False

    model: str = Field(default="cortecs/Meta-Llama-3-70B-Instruct-GPTQ-8b")
    base_url: str = Field(default="https://ecd9b66f-15d1-4efd-a7ef-5bc90c60883f.model-serving.eu01.onstackit.cloud/v1")
    api_key: str

    top_p: float = Field(default=0.1, title="LLM Top P")
    temperature: float = Field(default=0, title="LLM Temperature")
