from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import RunnableConfig

from rag_core_lib.chains.async_chain import AsyncChain


SummarizerInput = str
SummarizerOutput = str


class Summarizer(AsyncChain[SummarizerInput, SummarizerOutput], ABC):
    """Baseclass for summarizers."""

    @abstractmethod
    async def ainvoke(self, query: SummarizerInput, config: Optional[RunnableConfig] = None) -> SummarizerOutput:
        """
        Asynchronously invoke the summarizer with the given query and configuration.

        Parameters
        ----------
        query : SummarizerInput
            The input query for the summarizer.
        config : Optional[RunnableConfig], optional
            The configuration for the summarizer, by default None.

        Returns
        -------
        SummarizerOutput
            The output of the summarizer.
        """
