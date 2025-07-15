"""Module for the reranker interface."""

from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableConfig

RerankerInput = tuple[str, list[Document]]
RerankerOutput = list[Document]


class Reranker(Runnable[RerankerInput, RerankerOutput], ABC):
    """Reranker is an abstract base class that defines the interface for reranking operations.

    This class inherits from Runnable and ABC, and requires the implementation of an asynchronous reranking method.
    """

    @abstractmethod
    async def ainvoke(self, rerank_input: RerankerInput, config: Optional[RunnableConfig] = None) -> RerankerOutput:
        """
        Asynchronously invoke the reranker with the given input and configuration.

        Parameters
        ----------
        rerank_input : RerankerInput
            The input data for the reranker.
        config : Optional[RunnableConfig]
            The configuration for the reranker (default None).

        Returns
        -------
        RerankerOutput
            The output of the reranking process.
        """

    def invoke(self, rerank_input: RerankerInput, config: RunnableConfig | None = None) -> RerankerOutput:
        """
        Invoke the reranker with the given input and configuration.

        Parameters
        ----------
        rerank_input : RerankerInput
            The input data for the reranker.
        config : Optional[RunnableConfig]
            The configuration for the reranker (default None).

        Returns
        -------
        RerankerOutput
            The output of the reranking process.

        Raises
        ------
        NotImplementedError
            If this method is called, as it should use the async implementation.
        """
        raise NotImplementedError("Please use the async implementation.")
