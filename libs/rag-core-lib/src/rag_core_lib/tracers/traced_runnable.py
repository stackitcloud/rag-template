"""Module for the TracedGraph class."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig, ensure_config
from langfuse import get_client

from rag_core_lib.runnables.async_runnable import AsyncRunnable

RunnableInput = Any
RunnableOutput = Any


class TracedRunnable(AsyncRunnable[RunnableInput, RunnableOutput], ABC):
    """A class to represent a traced graph in an asynchronous chain.

    This class is designed to wrap around an inner Runnable chain and add tracing capabilities to it.
    It provides methods to asynchronously invoke the chain with tracing and to manage session IDs and tracing callbacks.

    Attributes
    ----------
    SESSION_ID_KEY : str
        The key used to store the session ID in the metadata.
    METADATA_KEY : str
        The key used to store metadata.
    """

    SESSION_ID_KEY = "session_id"
    METADATA_KEY = "metadata"

    def __init__(self, inner_chain: Runnable):
        """
        Initialize the TracedChain with an inner Runnable chain.

        Parameters
        ----------
        inner_chain : Runnable
            The inner chain to be traced.
        """
        self._inner_chain = inner_chain
        self.langfuse_client = get_client()

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        """
        Asynchronously invoke the chain with the given input and configuration.

        Parameters
        ----------
        chain_input : RunnableInput
            The input to be processed by the chain.
        config : Optional[RunnableConfig], optional
            Configuration for the chain execution (default None).
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        RunnableOutput
            The output produced by the chain after processing the input.

        """
        config = ensure_config(config)
        session_id = self._get_session_id(config)
        config_with_tracing = self._add_tracing_callback(config)
        with self.langfuse_client.start_as_current_span(name=self._inner_chain.__class__.__name__) as span:
            span.update_trace(session_id=session_id, input=chain_input)
            output = await self._inner_chain.ainvoke(chain_input, config=config_with_tracing)
            span.update_trace(output=output)
            return output

    @abstractmethod
    def _add_tracing_callback(self, config: Optional[RunnableConfig]) -> RunnableConfig: ...

    def _get_session_id(self, config: Optional[RunnableConfig]) -> str:
        return config.get(self.METADATA_KEY, {}).get(self.SESSION_ID_KEY, str(uuid.uuid4()))
