from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langgraph.graph import StateGraph

from rag_core_lib.chains.async_chain import AsyncChain


class GraphBase(AsyncChain[Input, Output], ABC):
    """
    Base class for a langgraph graph.
    """

    ERROR_MESSAGES_KEY = "error_messages"
    FINISH_REASONS = "finish_reasons"

    def __init__(self, graph_state_cls: Type[Any], graph_state_output_cls: Optional[Type[Any]] = None):
        self._state_graph = StateGraph(graph_state_cls, output=graph_state_output_cls)

    @abstractmethod
    async def ainvoke(self, graph_input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        ...

    @abstractmethod
    def _add_nodes(self) -> None:
        ...

    @abstractmethod
    def _wire_graph(self) -> None:
        ...

    def _setup_graph(self):
        self._add_nodes()
        self._wire_graph()
        return self._state_graph.compile()
