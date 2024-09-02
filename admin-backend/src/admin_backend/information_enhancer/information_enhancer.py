from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.documents import Document

RetrieverInput = list[Document]
RetrieverOutput = list[Document]


class InformationEnhancer(Runnable[RetrieverInput, RetrieverOutput], ABC):

    @abstractmethod
    def invoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        pass
