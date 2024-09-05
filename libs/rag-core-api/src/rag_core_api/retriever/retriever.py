from abc import ABC, abstractmethod

from langchain_core.documents import Document

from typing import Optional
from langchain_core.runnables import Runnable, RunnableConfig

RetrieverInput = str
RetrieverOutput = list[Document]


class Retriever(Runnable[RetrieverInput, RetrieverOutput], ABC):

    @abstractmethod
    def invoke(self, retriever_input: str, config: Optional[RunnableConfig] = None) -> list[Document]:
        pass
