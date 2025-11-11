"""Module for managing Langfuse prompts and Langfuse Language Models (LLMs)."""

import logging
from typing import Optional

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.llms import LLM
from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse.model import TextPromptClient
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

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
        managed_prompts: dict[str, ChatPromptTemplate],
        llm: LLM,
    ):
        """
        Initialize the LangfuseManager.

        Parameters
        ----------
        langfuse : Langfuse
            An instance of the Langfuse class.
        managed_prompts : dict of ChatPromptTemplate
            A dictionary where keys are strings and values are ChatPromptTemplate instances representing
            managed prompts.
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

        This method tries to fetch the prompt from Langfuse. If not found, it creates
        a new chat prompt from the local ChatPromptTemplate.

        Parameters
        ----------
        base_prompt_name : str
            The name of the base prompt to retrieve.

        Returns
        -------
        Optional[TextPromptClient]
            The Langfuse prompt client if found, None otherwise.
        """
        try:
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name, type="chat")
            return langfuse_prompt
        except NotFoundError:
            logger.info("Prompt '%s' not found in Langfuse. Creating new chat prompt.", base_prompt_name)

            local_prompt = self._managed_prompts[base_prompt_name]
            chat_messages = self._convert_chat_prompt_to_langfuse_format(local_prompt)

            # Get LLM config (excluding API keys)
            llm_configurable_configs = {
                config.id: config.default for config in self._llm.config_specs if self.API_KEY_FILTER not in config.id
            }

            self._langfuse.create_prompt(
                name=base_prompt_name,
                type="chat",
                prompt=chat_messages,
                config=llm_configurable_configs,
                labels=["production"],
            )

            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name, type="chat")
            return langfuse_prompt

        except Exception:
            logger.exception("Error occurred while getting prompt template from langfuse")
            return None

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

    def get_base_prompt(self, name: str) -> ChatPromptTemplate:
        """
        Retrieve the base prompt from managed prompts, with optional Langfuse integration.

        This method attempts to fetch the prompt from Langfuse. If found, it creates a
        ChatPromptTemplate with Langfuse metadata for proper tracing integration.
        If not found, it returns the fallback ChatPromptTemplate.

        Parameters
        ----------
        name : str
            The name of the prompt to retrieve.

        Returns
        -------
        ChatPromptTemplate
            The ChatPromptTemplate for the requested prompt, optionally with Langfuse metadata.
        """
        langfuse_prompt = self.get_langfuse_prompt(name)

        if langfuse_prompt:
            # For chat prompts, get_langchain_prompt() returns a list of messages
            # We need to convert this back to ChatPromptTemplate
            chat_messages = langfuse_prompt.get_langchain_prompt()

            langchain_messages = []
            for message in chat_messages:
                if isinstance(message, dict):
                    role = message.get("role")
                    content = message.get("content", "")
                elif isinstance(message, (list, tuple)) and len(message) >= 2:
                    role = message[0]
                    content = message[1] if len(message) > 1 else ""
                else:
                    logger.warning("Unexpected message format: %s", message)
                    continue

                if role == "system":
                    langchain_messages.append(SystemMessagePromptTemplate.from_template(content))
                elif role == "user":
                    langchain_messages.append(HumanMessagePromptTemplate.from_template(content))

            chat_prompt_template = ChatPromptTemplate.from_messages(langchain_messages)

            chat_prompt_template.metadata = {"langfuse_prompt": langfuse_prompt}

            return chat_prompt_template
        logger.error("Could not retrieve prompt template from langfuse. Using fallback value.")
        return self._managed_prompts[name]

    def _convert_chat_prompt_to_langfuse_format(self, chat_prompt: ChatPromptTemplate) -> list[dict]:
        """
        Convert a ChatPromptTemplate to Langfuse chat format.

        Parameters
        ----------
        chat_prompt : ChatPromptTemplate
            The ChatPromptTemplate to convert.

        Returns
        -------
        list[dict]
            A list of message dictionaries in Langfuse format.
        """
        chat_messages = []

        for message in chat_prompt.messages:
            # Convert SystemMessagePromptTemplate
            if hasattr(message, "prompt") and message.prompt.template:
                if message.__class__.__name__ == "SystemMessagePromptTemplate":
                    chat_messages.append({"role": "system", "content": message.prompt.template})
                elif message.__class__.__name__ == "HumanMessagePromptTemplate":
                    chat_messages.append({"role": "user", "content": message.prompt.template})
                elif message.__class__.__name__ == "AIMessagePromptTemplate":
                    chat_messages.append({"role": "assistant", "content": message.prompt.template})

        return chat_messages
