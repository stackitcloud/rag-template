from typing import Dict, Union

from pydantic_settings import BaseSettings
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import _SUPPORTED_PROVIDERS
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.runnables import ConfigurableField

from rag_core_lib.impl.settings.llm_provider_settings import BaseLLMProviderSettings
from rag_core_lib.impl.llm_config.llm_config_manager import LLMConfigManager

def extract_configurable_fields(settings: BaseSettings) -> Dict[str, ConfigurableField]:
    """
    Extract configurable fields from the given settings.

    Parameters
    ----------
    settings : BaseSettings
        Pydantic settings instance containing model field metadata.

    Returns
    -------
    Dict[str, ConfigurableField]
        Mapping from field name to ConfigurableField for fields with a title.

    Notes
    -----
    Uses getattr() to access the class attribute 'model_fields' so as to avoid
    instance-level deprecation warnings in Pydantic v2+ and static analysis tools.
    """
    fields: Dict[str, ConfigurableField] = {}
    cls = settings.__class__
    fields_meta = getattr(cls, "model_fields")
    for name, meta in fields_meta.items():
        if meta.title:
            fields[name] = ConfigurableField(id=name, name=meta.title)
    return fields


# Mapping of generic names to provider-specific kwarg keys
_PROVIDER_KEY_MAP: Dict[str, Dict[str, str]] = {
    "openai": {"api_key": "openai_api_key", "base_url": "openai_api_base"},
}


def chat_model_provider(
    settings: Union[BaseSettings, BaseLLMProviderSettings],
    provider: str = "openai",
) -> BaseLanguageModel:
    """
    Initialize a LangChain chat model with unified settings mapping and configurable fields.

    Parameters
    ----------
    settings : Union[BaseSettings, BaseLLMProviderSettings]
        Pydantic settings subclass containing at least 'model'.
    provider : str, optional
        Name of the chat model provider (default 'openai').

    Returns
    -------
    BaseLanguageModel
        Initialized chat model instance.

    Raises
    ------
    ValueError
        If 'model' is not defined in settings or if the provider is unsupported.
    """
    # Handle new provider settings
    if isinstance(settings, BaseLLMProviderSettings):
        model_name = settings.model
        data = settings.get_provider_kwargs()
        provider = settings.provider_name
    else:
        # Legacy handling
        data = settings.model_dump(exclude_none=True)
        model_name = data.pop("model", None)
        if not model_name:
            raise ValueError("'model' must be defined in settings")

        key_map = _PROVIDER_KEY_MAP.get(provider, {})
        for generic_key, specific_key in key_map.items():
            if generic_key in data:
                data[specific_key] = data.pop(generic_key)

    if provider not in _SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {_SUPPORTED_PROVIDERS}")

    chat = init_chat_model(
        model=model_name,
        model_provider=provider,
        **data,
    )
    config_fields = extract_configurable_fields(settings)
    if config_fields:
        chat = chat.configurable_fields(**config_fields)

    return chat


def create_chat_model_from_config(
    config_manager: LLMConfigManager,
    provider_name: str,
) -> BaseLanguageModel:
    """
    Create a chat model from the configuration manager.

    Parameters
    ----------
    config_manager : LLMConfigManager
        The configuration manager instance
    provider_name : str
        The name of the provider to use

    Returns
    -------
    BaseLanguageModel
        Initialized chat model instance
    """
    settings = config_manager.get_provider_settings(provider_name)
    langchain_provider = config_manager.get_langchain_provider_name(provider_name)
    
    return chat_model_provider(settings, langchain_provider)
