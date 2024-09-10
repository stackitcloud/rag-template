from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import Runnable, RunnableConfig

SummarizerInput = str
SummarizerOutput = str


class Summarizer(Runnable[SummarizerInput, SummarizerOutput], ABC):

    @abstractmethod
    def invoke(self, query: SummarizerInput, config: Optional[RunnableConfig] = None) -> SummarizerOutput:
        pass
