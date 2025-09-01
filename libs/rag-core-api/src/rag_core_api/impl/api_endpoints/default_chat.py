"""Module to define the DefaultChat class."""

from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.tracers.traced_runnable import TracedRunnable


class DefaultChat(Chat):
    """DefaultChat is a class that handles chat interactions using a traced graph."""

    def __init__(self, chat_graph: TracedRunnable):
        """
        Initialize the DefaultChat instance.

        Parameters
        ----------
        chat_graph : TracedGraph
            The traced graph representing the chat structure.
        """
        self._chat_graph = chat_graph

    async def achat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        """
        Asynchronously handles chat requests.

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
        config = RunnableConfig(
            tags=[],
            callbacks=None,
            recursion_limit=25,
            metadata={"session_id": session_id},
        )

        return await self._chat_graph.ainvoke(chat_request, config)
