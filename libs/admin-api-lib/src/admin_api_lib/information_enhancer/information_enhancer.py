from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document

from rag_core_lib.chains.async_chain import AsyncChain

RetrieverInput = list[Document]
RetrieverOutput = list[Document]


class InformationEnhancer(AsyncChain[RetrieverInput, RetrieverOutput], ABC):
    @abstractmethod
    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        pass
