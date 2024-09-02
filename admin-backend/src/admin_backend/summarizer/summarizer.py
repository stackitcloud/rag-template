from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import Runnable, RunnableConfig

RetrieverInput = str
RetrieverOutput = str


class Summarizer(Runnable[RetrieverInput, RetrieverOutput], ABC):

    @abstractmethod
    def invoke(self, query: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        pass
