"""Module for the GraphBase class."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langgraph.graph import StateGraph

from rag_core_lib.runnables.async_runnable import AsyncRunnable


class GraphBase(AsyncRunnable[Input, Output], ABC):
    """
    Base class for a langgraph graph.

    Attributes
    ----------
    ERROR_MESSAGES_KEY : str
        Key for error messages.
    FINISH_REASONS : str
        Key for finish reasons.
    """

    ERROR_MESSAGES_KEY = "error_messages"
    FINISH_REASONS = "finish_reasons"

    def __init__(self, graph_state_cls: Type[Any], graph_state_output_cls: Optional[Type[Any]] = None):
        """
        Initialize the GraphBase.

        Parameters
        ----------
        graph_state_cls : Type[Any]
            The class type for the graph state.
        graph_state_output_cls : Optional[Type[Any]]
            The class type for the graph state output, (default None).
        """
        self._state_graph = StateGraph(graph_state_cls, output=graph_state_output_cls)

    @abstractmethod
    async def ainvoke(self, graph_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Asynchronously invoke the graph with the given input and configuration.

        Parameters
        ----------
        graph_input : Input
            The input data for the graph.
        config : Optional[RunnableConfig], optional
            The configuration for running the graph, by default None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Output
            The output result from the graph execution.
        """

    @abstractmethod
    def _add_nodes(self) -> None: ...

    @abstractmethod
    def _wire_graph(self) -> None: ...

    def _setup_graph(self):
        self._add_nodes()
        self._wire_graph()
        return self._state_graph.compile()
