from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

from rag_core_api.impl.graph_state.graph_state import AnswerGraphState
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.chains.async_chain import AsyncChain


class ChatGraph(AsyncChain[AnswerGraphState, ChatResponse], ABC):
    """
    Base class for LLM answer generation graph.
    """

    @abstractmethod
    async def ainvoke(
        self, state: AnswerGraphState, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> ChatResponse: ...
