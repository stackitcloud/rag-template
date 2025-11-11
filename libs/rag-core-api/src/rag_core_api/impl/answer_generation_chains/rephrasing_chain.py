"""Module for rephrasing chain implementation."""

from typing import Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig

from rag_core_api.impl.graph.graph_state.graph_state import AnswerGraphState
from rag_core_lib.runnables.async_runnable import AsyncRunnable
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager

RunnableInput = AnswerGraphState
RunnableOutput = str


class RephrasingChain(AsyncRunnable[RunnableInput, RunnableOutput]):
    """Base class for rephrasing of the input question."""

    def __init__(self, langfuse_manager: LangfuseManager):
        """Initialize RephrasingChain with LangfuseManager.

        Parameters
        ----------
        langfuse_manager : LangfuseManager
            Manager for handling Langfuse operations and tracking.

        Returns
        -------
        None
        """
        self._langfuse_manager = langfuse_manager

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        """
        Asynchronously invokes the rephrasing chain.

        Parameters
        ----------
        chain_input : RunnableInput
            The input to be processed by the chain.
        config : Optional[RunnableConfig]
            Configuration for the chain execution (default None).
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        RunnableOutput
            The processed output from the chain.

        Notes
        -----
        This method creates a new chain instance before invocation.
        """
        return await self._create_chain().ainvoke(chain_input, config=config)

    def _create_chain(self) -> Runnable:
        return (
            self._langfuse_manager.get_base_prompt(self.__class__.__name__)
            | self._langfuse_manager.get_base_llm(self.__class__.__name__)
            | StrOutputParser()
        )
