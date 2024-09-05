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
        llm_instance = llm_class(**settings.dict())
        return llm_instance.configurable_fields(**configurable_fields)

    return factory


def get_configurable_fields_from(settings: LLMSettings) -> dict[str, ConfigurableField]:
    _fields = {}
    for field_name in settings.__fields__:
        settings_of_interest = settings.__fields__[field_name]
        if settings_of_interest.title is not None:
            _fields[field_name] = ConfigurableField(id=field_name, name=settings_of_interest.title)
    return _fields


def llm_provider(settings: LLMSettings, llm_cls: Type[LLM] = AlephAlpha) -> LLM:
    provider = _generic_llm_factory(llm_cls, get_configurable_fields_from(settings))
    return provider(settings)
