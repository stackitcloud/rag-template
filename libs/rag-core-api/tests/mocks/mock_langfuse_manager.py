"""Mock implementation of LangfuseManager for testing."""

from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.llms import LLM
from unittest.mock import Mock


class MockLangfuseManager:
    """Mock implementation of LangfuseManager for testing."""

    def __init__(self, langfuse: Mock, managed_prompts: dict, llm: LLM):
        self._langfuse = langfuse
        self._managed_prompts = managed_prompts
        self._llm = llm

    def init_prompts(self):
        """Mock init_prompts method."""
        pass

    def get_langfuse_prompt(self, base_prompt_name: str):
        """Mock get_langfuse_prompt method."""
        return self._managed_prompts[base_prompt_name]

    def get_base_llm(self, name: str) -> LLM:
        """Mock get_base_llm method."""
        return self._llm

    def get_base_prompt(self, name: str) -> ChatPromptTemplate:
        """Mock get_base_prompt method."""
        if name in self._managed_prompts:
            return self._managed_prompts[name]
        # Return a default ChatPromptTemplate if not found
        return ChatPromptTemplate.from_template("Default prompt template")
