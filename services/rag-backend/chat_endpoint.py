import logging
from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.tracers.traced_runnable import TracedRunnable

logger = logging.getLogger(__name__)


class UseCaseChat(Chat):
    def __init__(self, chat_graph: TracedRunnable):
        self._chat_graph = chat_graph

    async def achat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        config = RunnableConfig(
            tags=[],
            callbacks=None,
            recursion_limit=25,
            metadata={"session_id": session_id},
        )

        logger.info("Hold onto your hats, folks! The chat endpoint is now powered by UseCaseChat!")

        return await self._chat_graph.ainvoke(chat_request, config)
