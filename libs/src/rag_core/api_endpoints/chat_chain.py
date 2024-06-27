from abc import ABC, abstractmethod
from typing import Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse


class ChatChain(Runnable[ChatRequest, ChatResponse], ABC):
    """
    Base class for LLM answer generation chain.
    """

    @abstractmethod
    def invoke(self, input: ChatRequest, config: Optional[RunnableConfig] = None, **kwargs: Any) -> ChatResponse: ...
