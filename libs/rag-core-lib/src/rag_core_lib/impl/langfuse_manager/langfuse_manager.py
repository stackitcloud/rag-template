"""Module for managing Langfuse prompts and Langfuse Language Models (LLMs)."""

import logging
from typing import Optional

from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse.model import TextPromptClient

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
        llm: LLM,
    ):
        """
        Initialize the LangfuseManager.

        Parameters
        ----------
        langfuse : Langfuse
            An instance of the Langfuse class.
        managed_prompts : dict of str
            A dictionary where keys and values are strings representing managed prompts.
        llm : LLM
            An instance of the LLM class.
        """
        self._langfuse = langfuse
        self._llm = llm
        self._managed_prompts = managed_prompts

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
            llm_configurable_configs = {
                config.id: config.default for config in self._llm.config_specs if self.API_KEY_FILTER not in config.id
            }
            self._langfuse.create_prompt(
                name=base_prompt_name,
                prompt=self._managed_prompts[base_prompt_name],
                config=llm_configurable_configs,
                is_active=True,
            )
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name)
        except Exception as error:
            logger.error(
                "Error occured while getting prompt template from langfuse. Error:\n{error}",
                extra={error: error},
            )
            return None

        return langfuse_prompt

    def get_base_llm(self, name: str) -> LLM:
        """
        Get the Langfuse prompt, the configuration as well as Large Language Model (LLM).

        Parameters
        ----------
        name : str
            The name of the Langfuse prompt to retrieve the configuration for.

        Returns
        -------
        LLM
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
