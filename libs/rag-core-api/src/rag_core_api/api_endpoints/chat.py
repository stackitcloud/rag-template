from abc import ABC, abstractmethod

from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse


class Chat(ABC):
    """
    Base class for chat endpoint.
    """

    @abstractmethod
    async def achat(self, session_id: str, chat_request: ChatRequest) -> ChatResponse:
        ...
