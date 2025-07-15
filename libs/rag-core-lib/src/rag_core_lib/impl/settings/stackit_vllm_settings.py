"""Module contains settings regarding the STACKIT vLLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class StackitVllmSettings(BaseSettings):
    """
    Contains settings regarding the STACKIT vLLM.

    Attributes
    ----------
    model : str
        The model identifier.
    base_url : str
        The base URL for the model serving endpoint.
    api_key : str
        The API key for authentication.
    top_p : float
        Total probability mass of tokens to consider at each step.
    temperature : float
        What sampling temperature to use.
    """

    class Config:
        """Config class for reading Fields from env."""

        env_prefix = "STACKIT_VLLM_"
        case_sensitive = False

    model: str = Field(default="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic")
    base_url: str = Field(default="https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1")
    api_key: str

    top_p: float = Field(default=0.1, title="LLM Top P")
    temperature: float = Field(default=0, title="LLM Temperature")
