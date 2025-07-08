"""Module for managing Langfuse prompts and Langfuse Language Models (LLMs)."""

import logging
from typing import Optional, Union

from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.language_models.base import BaseLanguageModel
from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse.model import TextPromptClient

from rag_core_lib.impl.llm_config.llm_config_manager import LLMConfigManager

logger = logging.getLogger(__name__)


class LangfuseManager:
    """Manage prompts using Langfuse and a Large Language Model (LLM).

    Attributes
    ----------
    API_KEY_FILTER : str
        A filter string used to exclude the API key from configurations.
    """

    API_KEY_FILTER: str = "api_key"

    def __init__(
        self,
        langfuse: Langfuse,
        managed_prompts: dict[str, str],
        llm: Union[LLM, BaseLanguageModel],
        llm_config_manager: Optional[LLMConfigManager] = None,
        provider_name: Optional[str] = None,
    ):
        """
        Initialize the LangfuseManager.

        Parameters
        ----------
        langfuse : Langfuse
            An instance of the Langfuse class.
        managed_prompts : dict of str
            A dictionary where keys and values are strings representing managed prompts.
        llm : Union[LLM, BaseLanguageModel]
            An instance of the LLM or BaseLanguageModel class.
        llm_config_manager : Optional[LLMConfigManager]
            Configuration manager for LLM providers.
        provider_name : Optional[str]
            The name of the LLM provider for enhanced configuration.
        """
        self._langfuse = langfuse
        self._llm = llm
        self._managed_prompts = managed_prompts
        self._llm_config_manager = llm_config_manager
        self._provider_name = provider_name

    def init_prompts(self) -> None:
        """
        Initialize the prompts managed by the LangfuseManager.

        This method iterates over the keys of the managed prompts and retrieves
        each prompt using the `get_langfuse_prompt` method.

        Returns
        -------
        None
        """
        for key in list(self._managed_prompts.keys()):
            self.get_langfuse_prompt(key)

    def get_langfuse_prompt(self, base_prompt_name: str) -> Optional[TextPromptClient]:
        """
        Retrieve the prompt from Langfuse Prompt Management.

        Parameters
        ----------
        base_prompt_name : str
            The name of the base prompt to retrieve.

        Returns
        -------
        Optional[TextPromptClient]
            The Langfuse prompt template if found, otherwise None.

        Raises
        ------
        NotFoundError
            If the prompt is not found in Langfuse, a new prompt is created.
        Exception
            If an error occurs while retrieving the prompt template from Langfuse.
        """
        try:
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name)
        except NotFoundError:
            logger.info("Prompt not found in LangFuse. Creating new.")
            llm_configurable_configs = self._get_llm_configurable_configs()
            self._langfuse.create_prompt(
                name=base_prompt_name,
                prompt=self._managed_prompts[base_prompt_name],
                config=llm_configurable_configs,
                labels=["production"],
            )
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name)
        except Exception as error:
            logger.error(
                "Error occured while getting prompt template from langfuse. Error:\n{error}",
                extra={error: error},
            )
            return None

        return langfuse_prompt

    def _get_llm_configurable_configs(self) -> dict:
        """
        Get LLM configurable configurations.

        Returns
        -------
        dict
            Dictionary of configurable parameters for the LLM
        """
        if self._llm_config_manager and self._provider_name:
            # Use enhanced configuration manager
            configurable_fields = self._llm_config_manager.get_configurable_fields(self._provider_name)
            settings = self._llm_config_manager.get_provider_settings(self._provider_name)

            # Convert to format expected by Langfuse
            configs = {}
            for field_name, display_name in configurable_fields.items():
                if hasattr(settings, field_name):
                    configs[field_name] = getattr(settings, field_name)

            return configs
        else:
            # Legacy handling - use config_specs if available
            if hasattr(self._llm, 'config_specs'):
                return {
                    config.id: config.default
                    for config in self._llm.config_specs
                    if self.API_KEY_FILTER not in config.id
                }
            return {}

    def get_base_llm(self, name: str) -> Union[LLM, BaseLanguageModel]:
        """
        Get the Langfuse prompt, the configuration as well as Large Language Model (LLM).

        Parameters
        ----------
        name : str
            The name of the Langfuse prompt to retrieve the configuration for.

        Returns
        -------
        Union[LLM, BaseLanguageModel]
            The base Large Language Model. If the Langfuse prompt is not found,
            returns the LLM with a fallback configuration.
        """
        langfuse_prompt = self.get_langfuse_prompt(name)
        if not langfuse_prompt:
            logger.error("Using fallback for llm")
            return self._llm

        return self._llm.with_config({"configurable": langfuse_prompt.config})

    def get_base_prompt(self, name: str) -> PromptTemplate:
        """
        Retrieve the base prompt from Langfuse Prompt Management.

        Parameters
        ----------
        name : str
            The name of the prompt to retrieve.

        Returns
        -------
        PromptTemplate
            The base prompt template.

        Notes
        -----
        If the prompt cannot be retrieved from Langfuse, a fallback value is used.
        """
        langfuse_prompt = self.get_langfuse_prompt(name)
        if not langfuse_prompt:
            logger.error("Could not retrieve prompt template from langfuse. Using fallback value.")
            return PromptTemplate.from_template(self._managed_prompts[name])

        langchain_prompt = langfuse_prompt.get_langchain_prompt()
        return PromptTemplate.from_template(langchain_prompt)
