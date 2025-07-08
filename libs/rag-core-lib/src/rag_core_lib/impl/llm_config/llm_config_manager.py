"""Module for managing LLM configurations across different providers."""

from typing import Dict, Type, Any, Union
from pydantic import Field
from pydantic_settings import BaseSettings

from rag_core_lib.impl.settings.llm_provider_settings import (
    BaseLLMProviderSettings,
    StackitProviderSettings,
    OllamaProviderSettings,
    GeminiProviderSettings
)
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings
from rag_core_lib.impl.settings.ollama_llm_settings import OllamaSettings


class LLMProviderConfig(BaseSettings):
    """
    Configuration for LLM providers.
    
    This class manages the configuration for different LLM providers,
    allowing dynamic selection and configuration based on the provider type.
    
    Attributes
    ----------
    provider : str
        The name of the LLM provider to use
    config : Dict[str, Any]
        Provider-specific configuration parameters
    """
    
    class Config:
        """Config class for reading Fields from env."""
        env_prefix = "LLM_PROVIDER_"
        case_sensitive = False
    
    provider: str = Field(default="stackit", title="LLM Provider")
    config: Dict[str, Any] = Field(default_factory=dict)


class LLMConfigManager:
    """
    Manager for LLM configurations across different providers.
    
    This class provides a centralized way to manage and configure
    different LLM providers with their specific settings.
    """
    
    # Registry of available provider settings classes
    PROVIDER_SETTINGS: Dict[str, Type[BaseLLMProviderSettings]] = {
        "stackit": StackitProviderSettings,
        "gemini": GeminiProviderSettings,
        "ollama": OllamaProviderSettings,
    }
    
    # Legacy settings mapping for backward compatibility
    LEGACY_SETTINGS: Dict[str, Type[BaseSettings]] = {
        "stackit_legacy": StackitVllmSettings,
        "ollama_legacy": OllamaSettings,
    }
    
    def __init__(self, config_map: Dict[str, Dict[str, Any]]):
        """
        Initialize the LLM Config Manager.
        
        Parameters
        ----------
        config_map : Dict[str, Dict[str, Any]]
            Configuration map from values.yaml containing provider configurations
        """
        self.config_map = config_map
        self._provider_instances: Dict[str, BaseLLMProviderSettings] = {}
    
    def get_provider_settings(self, provider_name: str) -> Union[BaseLLMProviderSettings, BaseSettings]:
        """
        Get provider settings instance for the specified provider.
        
        Parameters
        ----------
        provider_name : str
            The name of the provider
            
        Returns
        -------
        Union[BaseLLMProviderSettings, BaseSettings]
            The provider settings instance
            
        Raises
        ------
        ValueError
            If the provider is not supported
        """
        if provider_name in self._provider_instances:
            return self._provider_instances[provider_name]
        
        # Check new provider settings first
        if provider_name in self.PROVIDER_SETTINGS:
            settings_class = self.PROVIDER_SETTINGS[provider_name]
            provider_config = self.config_map.get(provider_name, {})
            settings = settings_class(**provider_config)
            self._provider_instances[provider_name] = settings
            return settings
        
        # Fall back to legacy settings for backward compatibility
        if provider_name in self.LEGACY_SETTINGS:
            settings_class = self.LEGACY_SETTINGS[provider_name]
            # For legacy, instantiate directly (they have their own env loading)
            settings = settings_class()
            self._provider_instances[provider_name] = settings
            return settings
        
        raise ValueError(f"Unsupported provider: {provider_name}. "
                        f"Supported providers: {list(self.PROVIDER_SETTINGS.keys()) + list(self.LEGACY_SETTINGS.keys())}")
    
    def get_langchain_provider_name(self, provider_name: str) -> str:
        """
        Get the LangChain provider name for the given provider.
        
        Parameters
        ---------- 
        provider_name : str
            The internal provider name
            
        Returns
        -------
        str
            The LangChain provider name
        """
        provider_mapping = {
            "stackit": "openai",  # STACKIT uses OpenAI-compatible API
            "stackit_legacy": "openai",  # Legacy STACKIT also uses OpenAI-compatible API
            "gemini": "google-genai",  # Google Gemini provider
            "ollama": "ollama",
            "ollama_legacy": "ollama", 
        }
        return provider_mapping.get(provider_name, provider_name)
    
    def get_configurable_fields(self, provider_name: str) -> Dict[str, str]:
        """
        Get configurable fields for Langfuse for the specified provider.
        
        Parameters
        ----------
        provider_name : str
            The name of the provider
            
        Returns
        -------
        Dict[str, str]
            Mapping of field names to display names
        """
        settings = self.get_provider_settings(provider_name)
        
        if hasattr(settings, 'get_configurable_fields'):
            return settings.get_configurable_fields()
        
        # For legacy settings, extract from model fields
        from rag_core_lib.impl.llms.llm_factory import extract_configurable_fields
        from langchain_core.runnables import ConfigurableField
        fields = extract_configurable_fields(settings)
        return {name: field.name for name, field in fields.items() if isinstance(field, ConfigurableField)}
    
    def list_available_providers(self) -> Dict[str, str]:
        """
        List all available providers with descriptions.
        
        Returns
        -------
        Dict[str, str]
            Mapping of provider names to descriptions
        """
        return {
            "stackit": "STACKIT vLLM service",
            "gemini": "Google Gemini models",
            "ollama": "Local Ollama models",
            "stackit_legacy": "STACKIT vLLM service (legacy)",
            "ollama_legacy": "Legacy Ollama configuration",
        }
    
    @classmethod
    def from_values_yaml(cls, values_config: Dict[str, Any]) -> "LLMConfigManager":
        """
        Create LLMConfigManager from values.yaml configuration.
        
        Parameters
        ----------
        values_config : Dict[str, Any]
            The configuration from values.yaml
            
        Returns
        -------
        LLMConfigManager
            Configured manager instance
        """
        # Extract LLM provider configurations from values.yaml structure
        backend_envs = values_config.get("backend", {}).get("envs", {})
        
        config_map = {}
        
        # Map existing configurations to new structure
        if "stackitVllm" in backend_envs:
            stackit_config = backend_envs["stackitVllm"]
            config_map["stackit"] = {
                "model": stackit_config.get("STACKIT_VLLM_MODEL", "gpt-3.5-turbo"),
                "base_url": stackit_config.get("STACKIT_VLLM_BASE_URL"),
                "api_key": values_config.get("backend", {}).get("secrets", {}).get("stackitVllm", {}).get("apiKey", ""),
            }
        
        if "ollama" in backend_envs:
            ollama_config = backend_envs["ollama"]
            config_map["ollama"] = {
                "model": ollama_config.get("OLLAMA_MODEL", "llama3:instruct"),
                "base_url": ollama_config.get("OLLAMA_BASE_URL", "http://localhost:11434"),
                "temperature": float(ollama_config.get("OLLAMA_TEMPERATURE", 0.0)),
                "top_k": int(ollama_config.get("OLLAMA_TOP_K", 0)),
                "top_p": float(ollama_config.get("OLLAMA_TOP_P", 0.0)),
            }
        
        return cls(config_map)
