from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig

from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse


class ChatChain(Runnable[ChatRequest, ChatResponse], ABC):
    """
    Base class for LLM answer generation chain.
    """

    @abstractmethod
    def invoke(self, input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any) -> ChatResponse: ...
