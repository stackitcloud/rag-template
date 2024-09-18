from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.chains.async_chain import AsyncChain


class ChatChain(AsyncChain[ChatRequest, ChatResponse], ABC):
    """
    Base class for LLM answer generation chain.
    """

    @abstractmethod
    async def ainvoke(
        self, chain_input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> ChatResponse: ...
