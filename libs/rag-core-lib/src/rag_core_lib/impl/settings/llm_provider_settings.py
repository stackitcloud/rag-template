"""Module containing generic LLM provider settings and configuration."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class BaseLLMProviderSettings(BaseSettings, ABC):
    """
    Base class for LLM provider settings.

    This abstract base class defines the common interface that all LLM provider
    settings classes should implement. It ensures consistent configuration
    across different providers while allowing provider-specific customization.

    Attributes
    ----------
    model : str
        The model name/identifier for the LLM
    provider_name : str
        The name of the provider (e.g., 'openai', 'ollama', 'anthropic')
    """

    model: str
    provider_name: str

    @abstractmethod
    def get_provider_kwargs(self) -> Dict[str, Any]:
        """
        Get provider-specific keyword arguments.

        This method should return a dictionary of keyword arguments
        that are specific to the provider's API.

        Returns
        -------
        Dict[str, Any]
            Provider-specific configuration parameters
        """
        pass

    @abstractmethod
    def get_configurable_fields(self) -> Dict[str, str]:
        """
        Get fields that should be configurable in Langfuse.

        Returns
        -------
        Dict[str, str]
            Mapping of field names to their display names for Langfuse
        """
        pass





class OllamaProviderSettings(BaseLLMProviderSettings):
    """
    Settings for Ollama local models.

    Attributes
    ----------
    model : str
        The model identifier (e.g., 'llama3:instruct')
    base_url : str
        The base URL for the Ollama API
    temperature : float
        Sampling temperature
    top_k : int
        Top-k sampling parameter
    top_p : float
        Nucleus sampling parameter
    """

    class Config:
        """Config class for reading Fields from env."""
        env_prefix = "OLLAMA_"
        case_sensitive = False

    provider_name: str = Field(default="ollama", exclude=True)
    base_url: str = Field(default="http://localhost:11434")
    temperature: float = Field(default=0.0, title="LLM Temperature")
    top_k: int = Field(default=0, title="LLM Top K")
    top_p: float = Field(default=0.0, title="LLM Top P")

    def get_provider_kwargs(self) -> Dict[str, Any]:
        """Get Ollama-specific keyword arguments."""
        return self.model_dump(exclude={"provider_name"})

    def get_configurable_fields(self) -> Dict[str, str]:
        """Get configurable fields for Langfuse."""
        return {
            "temperature": "LLM Temperature",
            "top_k": "LLM Top K",
            "top_p": "LLM Top P",
        }


class StackitProviderSettings(BaseLLMProviderSettings):
    """
    Settings for STACKIT vLLM service.

    STACKIT uses OpenAI-compatible API, providing llama and other models
    through a standardized REST API interface.

    Attributes
    ----------
    model : str
        The model identifier (e.g., 'cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic')
    api_key : str
        The API key for authentication
    base_url : str
        The base URL for the STACKIT vLLM API
    temperature : float
        Sampling temperature
    max_tokens : Optional[int]
        Maximum number of tokens to generate
    top_p : float
        Nucleus sampling parameter
    frequency_penalty : float
        Frequency penalty parameter
    presence_penalty : float
        Presence penalty parameter
    """

    class Config:
        """Config class for reading Fields from env."""
        env_prefix = "STACKIT_VLLM_"
        case_sensitive = False

    provider_name: str = Field(default="openai", exclude=True)  # Uses OpenAI-compatible API
    model: str = Field(default="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic")
    api_key: str
    base_url: str = Field(
        default="https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1"
    )
    temperature: float = Field(default=0.0, title="LLM Temperature")
    max_tokens: Optional[int] = Field(default=None, title="LLM Max Tokens")
    top_p: float = Field(default=0.1, title="LLM Top P")
    frequency_penalty: float = Field(default=0.0, title="LLM Frequency Penalty")
    presence_penalty: float = Field(default=0.0, title="LLM Presence Penalty")

    def get_provider_kwargs(self) -> Dict[str, Any]:
        """Get STACKIT-specific keyword arguments."""
        kwargs = self.model_dump(exclude={"provider_name"})
        # Convert to OpenAI-compatible parameter names
        if "api_key" in kwargs:
            kwargs["openai_api_key"] = kwargs.pop("api_key")
        return kwargs

    def get_configurable_fields(self) -> Dict[str, str]:
        """Get configurable fields for Langfuse."""
        return {
            "temperature": "LLM Temperature",
            "max_tokens": "LLM Max Tokens",
            "top_p": "LLM Top P",
            "frequency_penalty": "LLM Frequency Penalty",
            "presence_penalty": "LLM Presence Penalty",
        }


class GeminiProviderSettings(BaseLLMProviderSettings):
    """
    Settings for Google Gemini models.

    Attributes
    ----------
    model : str
        The model identifier (e.g., 'gemini-1.5-pro', 'gemini-1.5-flash')
    api_key : str
        The Google API key
    temperature : float
        Sampling temperature (0.0 to 2.0)
    max_output_tokens : Optional[int]
        Maximum number of tokens to generate
    top_p : float
        Nucleus sampling parameter
    top_k : int
        Top-k sampling parameter
    """

    class Config:
        """Config class for reading Fields from env."""
        env_prefix = "GEMINI_"
        case_sensitive = False

    provider_name: str = Field(default="gemini", exclude=True)
    api_key: str
    temperature: float = Field(default=0.7, title="LLM Temperature")
    max_output_tokens: Optional[int] = Field(default=None, title="LLM Max Output Tokens")
    top_p: float = Field(default=0.95, title="LLM Top P")
    top_k: int = Field(default=40, title="LLM Top K")

    def get_provider_kwargs(self) -> Dict[str, Any]:
        """Get Gemini-specific keyword arguments."""
        kwargs = self.model_dump(exclude={"provider_name"})
        # Convert to Google AI-specific parameter names
        if "api_key" in kwargs:
            kwargs["google_api_key"] = kwargs.pop("api_key")
        return kwargs

    def get_configurable_fields(self) -> Dict[str, str]:
        """Get configurable fields for Langfuse."""
        return {
            "temperature": "LLM Temperature",
            "max_output_tokens": "LLM Max Output Tokens",
            "top_p": "LLM Top P",
            "top_k": "LLM Top K",
        }
