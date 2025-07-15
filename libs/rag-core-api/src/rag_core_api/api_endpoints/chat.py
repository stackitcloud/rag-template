"""Module for base class of chat endpoint."""

from abc import ABC, abstractmethod

from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse


class Chat(ABC):
    """Base class for chat endpoint."""

    @abstractmethod
    async def achat(self, session_id: str, chat_request: ChatRequest) -> ChatResponse:
        """
        Abstract method to handle asynchronous chat requests.

        Parameters
        ----------
        session_id : str
            The unique identifier for the chat session.
        chat_request : ChatRequest
            The request object containing the chat details.

        Returns
        -------
        ChatResponse
            The response object containing the chat results.
        """
