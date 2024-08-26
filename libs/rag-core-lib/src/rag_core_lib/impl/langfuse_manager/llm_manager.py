import logging

from langchain_core.language_models.llms import LLM

from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager

logger = logging.getLogger(__name__)


class LangfuseLLMManager:
    """
    Manager class for Langfuse Language Model (LLM).
    """

    BASE_PROMPT_NAME: str = "base-answer-generation"

    def __init__(
        self,
        langfuse_manager: LangfuseManager,
        llm: LLM,
    ):
        self._llm = llm
        self._langfuse_manager = langfuse_manager

    def get_base_llm(self) -> LLM:
        """
        Get the base Langfuse Language Model (LLM).

        Returns:
            LLM: The base Langfuse Language Model.
        """
        langfuse_prompt = self._langfuse_manager.get_langfuse_prompt(self.BASE_PROMPT_NAME)
        if not langfuse_prompt:
            logger.error("Using fallback for llm")
            return self._llm

        return self._llm.with_config({"configurable": langfuse_prompt.config})
