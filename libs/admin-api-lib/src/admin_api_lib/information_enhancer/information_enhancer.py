"""Module for the InformationEnhancer abstract base class."""

from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from rag_core_lib.runnables.async_runnable import AsyncRunnable

RetrieverInput = list[Document]
RetrieverOutput = list[Document]


class InformationEnhancer(AsyncRunnable[RetrieverInput, RetrieverOutput], ABC):
    """The base class for an information enhancer."""

    @abstractmethod
    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        """
        Asynchronously invokes the information enhancer with the given input and configuration.

        Parameters
        ----------
        information : RetrieverInput
            The input information to be processed by the information enhancer.
        config : Optional[RunnableConfig]
            The configuration settings for the information enhancer, by default None.

        Returns
        -------
        RetrieverOutput
            The output after processing the input information.
        """
