"""Module for the Retriever class."""

from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableConfig

RetrieverInput = str
RetrieverOutput = list[Document]


class Retriever(Runnable[RetrieverInput, RetrieverOutput], ABC):
    """Retriever is an abstract base class that defines the interface for a retriever component.

    It inherits from Runnable and ABC, and provides both synchronous and asynchronous methods
    for invoking the retriever with a given input and configuration.
    """

    @abstractmethod
    async def ainvoke(self, retriever_input: str, config: Optional[RunnableConfig] = None) -> list[Document]:
        """
        Asynchronously invoke the retriever with the given input and configuration.

        Parameters
        ----------
        retriever_input : str
            The input string to be processed by the retriever.
        config : Optional[RunnableConfig]
            An configuration object for the retriever (default None).

        Returns
        -------
        list[Document]
            A list of Document objects retrieved based on the input and configuration.
        """

    def invoke(self, retriever_input: list[float], config: RunnableConfig | None = None) -> list[Document]:
        """
        Invoke the retriever with the given input and configuration.

        Parameters
        ----------
        retriever_input : list[float]
            A list of floating-point numbers representing the input to the retriever.
        config : RunnableConfig, optional
            An optional configuration for the retriever. (default None)

        Returns
        -------
        list[Document]
            A list of Document objects retrieved based on the input and configuration.

        Raises
        ------
        NotImplementedError
            This method is not implemented and should use the async implementation instead.
        """
        raise NotImplementedError("Please use the async implementation.")
