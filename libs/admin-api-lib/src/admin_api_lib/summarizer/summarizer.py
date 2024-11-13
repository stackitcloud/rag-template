from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import RunnableConfig

from rag_core_lib.chains.async_chain import AsyncChain


SummarizerInput = str
SummarizerOutput = str


class Summarizer(AsyncChain[SummarizerInput, SummarizerOutput], ABC):
    @abstractmethod
    async def ainvoke(self, query: SummarizerInput, config: Optional[RunnableConfig] = None) -> SummarizerOutput:
        pass
