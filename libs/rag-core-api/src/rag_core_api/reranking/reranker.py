from abc import ABC, abstractmethod

from langchain_core.documents import Document

from typing import Optional, Tuple
from langchain_core.runnables import Runnable, RunnableConfig


RerankerInput = Tuple[str, list[Document]]
RerankerOutput = list[Document]


class Reranker(Runnable[RerankerInput, RerankerOutput], ABC):

    @abstractmethod
    def invoke(self, rerank_input: RerankerInput, config: Optional[RunnableConfig] = None) -> RerankerOutput:
        pass
