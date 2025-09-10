"""The Module for the use case chat endpoint implementation."""

import logging
from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.tracers.traced_runnable import TracedRunnable

logger = logging.getLogger(__name__)


class UseCaseChat(Chat):
    """The class of the chat use case implementation."""

    def __init__(self, chat_graph: TracedRunnable):
        """Initialize the use case chat.

        Parameters
        ----------
        chat_graph : TracedRunnable
            The chat graph to use for this use case.
        """
        self._chat_graph = chat_graph

    async def achat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        """Handle a chat request.

        Parameters
        ----------
        session_id : str
            The ID of the session.
        chat_request : ChatRequest
            The chat request to handle.

        Returns
        -------
        ChatResponse
            The response to the chat request.
        """
        config = RunnableConfig(
            tags=[],
            callbacks=None,
            recursion_limit=25,
            metadata={"session_id": session_id},
        )

        logger.info("Hold onto your hats, folks! The chat endpoint is now powered by UseCaseChat!")

        return await self._chat_graph.ainvoke(chat_request, config)
