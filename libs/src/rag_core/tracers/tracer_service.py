from abc import ABC, abstractmethod

from langchain_core.language_models.llms import LLM
from langchain_core.runnables import RunnableConfig


class TracerService(ABC):
    """
    Abstract service for generating tracer-specific configurations for LLM chains.
    """
    #TODO: dissolve the prompt from tracing service

    @abstractmethod
    def get_tracer_config(self, session_id: str) -> RunnableConfig:
        """
        Creates a tracer configuration for an LLM chain.

        Parameters
        ----------
        session_id : str
            The session identifier.

        Returns
        -------
        RunnableConfig
            The configuration for the LLM chain.
        """

    @abstractmethod
    def get_base_prompt(self):
        """
        Retrieves the base prompt from Langfuse Prompt Management.
        """

    @abstractmethod
    def get_base_llm(self) -> LLM:
        """"""
