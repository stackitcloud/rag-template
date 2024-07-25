from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

from rag_core_api.api_endpoints.chat_chain import ChatChain
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse


class ExampleReplacementChatChain(ChatChain):

    def invoke(self, input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any) -> ChatResponse:
        return ChatResponse(
            answer="This is just for testing purposes.",
            finish_reason="Random",
            citations=[],
        )
