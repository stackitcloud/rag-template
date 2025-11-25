"""Module for the use case chat endpoint."""

import logging
from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.tracers.traced_runnable import TracedRunnable

logger = logging.getLogger(__name__)


class UseCaseChat(Chat):
    """Use case chat endpoint implementation."""

    def __init__(self, chat_graph: TracedRunnable):
        self._chat_graph = chat_graph

    async def achat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        """
        Handle a chat request and return a chat response.

        Parameters
        ----------
        session_id : str
            The session identifier for the chat.
        chat_request : ChatRequest
            The chat request data.

        Returns
        -------
        ChatResponse
            The chat response.
        """
        config = RunnableConfig(
            tags=[],
            callbacks=None,
            recursion_limit=25,
            metadata={"session_id": session_id},
        )

        logger.info("Hold onto your hats, folks! The chat endpoint is now powered by UseCaseChat!")

        return await self._chat_graph.ainvoke(chat_request, config)
