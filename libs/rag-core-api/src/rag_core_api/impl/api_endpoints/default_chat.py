from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_lib.tracers.traced_chain import TracedGraph


class DefaultChat(Chat):
    def __init__(self, chat_graph: TracedGraph):
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

        return await self._chat_graph.ainvoke(chat_request, config)
