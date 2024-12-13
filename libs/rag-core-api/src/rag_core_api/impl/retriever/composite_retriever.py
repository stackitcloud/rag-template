import logging
from copy import deepcopy
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig

from rag_core_api.impl.retriever.retriever_quark import RetrieverQuark
from rag_core_api.reranking.reranker import Reranker
from rag_core_api.retriever.retriever import Retriever
from rag_core_lib.impl.data_types.content_type import ContentType

logger = logging.getLogger(__name__)


class CompositeRetriever(Retriever):
    def __init__(
        self,
        retrievers: list[RetrieverQuark],
        reranker: Optional[Reranker],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._reranker = reranker
        self._retrievers = retrievers

    def verify_readiness(self) -> None:
        """Check if the vector db contains a non-empty collection with the expected name."""
        for retriever in self._retrievers:
            retriever.verify_readiness()

    async def ainvoke(
        self, retriever_input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list[Document]:
        results = []
        if config is None:
            config = RunnableConfig(metadata={"filter_kwargs": {}})
        for retriever in self._retrievers:
            tmp_config = deepcopy(config)
            results += await retriever.ainvoke(retriever_input, config=tmp_config)

        # remove summaries
        results = [x for x in results if x.metadata["type"] != ContentType.SUMMARY.value]

        # remove duplicated entries
        return_val = []
        for result in results:
            if result.metadata["id"] in [x.metadata["id"] for x in return_val]:
                continue
            return_val.append(result)

        if self._reranker:
            return_val = await self._reranker.ainvoke((return_val, retriever_input), config=config)

        return return_val
