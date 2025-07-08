from pydantic_settings import BaseSettings
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import _SUPPORTED_PROVIDERS
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.runnables import ConfigurableField


def extract_configurable_fields(settings: BaseSettings) -> dict[str, ConfigurableField]:
    """
    Extract configurable fields from the given settings.

    Parameters
    ----------
    settings : BaseSettings
        Pydantic settings instance containing model field metadata.

    Returns
    -------
    dict[str, ConfigurableField]
        Mapping from field name to ConfigurableField for fields with a title.

    Notes
    -----
    Uses getattr() to access the class attribute 'model_fields' so as to avoid
    instance-level deprecation warnings in Pydantic v2+ and static analysis tools.
    """
    fields: dict[str, ConfigurableField] = {}
    cls = settings.__class__
    fields_meta = getattr(cls, "model_fields")
    for name, meta in fields_meta.items():
        if meta.title:
            fields[name] = ConfigurableField(id=name, name=meta.title)
    return fields


# Mapping of generic names to provider-specific kwarg keys
_PROVIDER_KEY_MAP: dict[str, dict[str, str]] = {
    "openai": {"api_key": "openai_api_key", "base_url": "openai_api_base"},
}


def chat_model_provider(
    settings: BaseSettings,
    provider: str = "openai",
) -> BaseLanguageModel:
    """
    Initialize a LangChain chat model with unified settings mapping and configurable fields.

    Parameters
    ----------
    settings : BaseSettings
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
        return chat.configurable_fields(**config_fields)

    return chat
