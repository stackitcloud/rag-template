import logging

from langchain.prompts import PromptTemplate
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager


logger = logging.getLogger(__name__)


class LangfusePromptManager:
    """
    Manager class for handling Langfuse prompts.
    """

    BASE_PROMPT_NAME: str = "base-answer-generation"
    API_KEY_FILTER: str = "api_key"

    def __init__(self, base_answer_generation_prompt: PromptTemplate, langfuse_manager: LangfuseManager):
        self._base_answer_generation_prompt = base_answer_generation_prompt
        self._langfuse_manager = langfuse_manager

    def get_base_prompt(self) -> PromptTemplate:
        """
        Retrieves the base prompt from Langfuse Prompt Management.

        Returns:
            PromptTemplate: The base prompt template.
        """
        langfuse_prompt = self._langfuse_manager.get_langfuse_prompt(self.BASE_PROMPT_NAME)
        if not langfuse_prompt:
            logger.error("Could not retrieve prompt template from langfuse. Using fallback value.")
            return PromptTemplate.from_template(self._base_answer_generation_prompt.template)

        langchain_prompt = langfuse_prompt.get_langchain_prompt()
        return PromptTemplate.from_template(langchain_prompt)
