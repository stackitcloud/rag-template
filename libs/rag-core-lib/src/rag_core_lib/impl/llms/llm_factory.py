"""Module for creating LLM instances from settings and the LLM class."""

from typing import Callable, Type

from langchain_community.llms.aleph_alpha import AlephAlpha
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import ConfigurableField

from rag_core_lib.impl.settings.llm_settings import LLMSettings


def _generic_llm_factory(
    llm_class: Type[LLM],
    configurable_fields: dict[str, ConfigurableField],
) -> Callable[[LLMSettings], LLM]:
    def factory(settings: LLMSettings) -> LLM:
        llm_instance = llm_class(**settings.model_dump())
        return llm_instance.configurable_fields(**configurable_fields)

    return factory


def get_configurable_fields_from(settings: LLMSettings) -> dict[str, ConfigurableField]:
    """
    Extract configurable fields from the given LLMSettings.

    Parameters
    ----------
    settings : LLMSettings
        An instance of LLMSettings containing model fields with their respective settings.

    Returns
    -------
    dict[str, ConfigurableField]
        A dictionary where the keys are field names and the values are ConfigurableField instances
        with the field's id and name set based on the settings.

    Notes
    -----
    Only fields with a non-None title in their settings are included in the returned dictionary.
    """
    _fields = {}
    for field_name in settings.model_fields:
        settings_of_interest = settings.model_fields[field_name]
        if settings_of_interest.title is not None:
            _fields[field_name] = ConfigurableField(id=field_name, name=settings_of_interest.title)
    return _fields


def llm_provider(settings: LLMSettings, llm_cls: Type[LLM] = AlephAlpha) -> LLM:
    """
    Create an instance of a LLM provider based on the given settings and class type.

    Parameters
    ----------
    settings : LLMSettings
        Configuration settings for the LLM.
    llm_cls : Type[LLM], optional
        The class type of the LLM to instantiate (default AlephAlpha).

    Returns
    -------
    LLM
        An instance of the specified language model provider.
    """
    provider = _generic_llm_factory(llm_cls, get_configurable_fields_from(settings))
    return provider(settings)
