"""Module for the CompositeRetriever class."""

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
    """CompositeRetriever class that combines multiple retrievers and optionally reranks the results."""

    def __init__(
        self,
        retrievers: list[RetrieverQuark],
        reranker: Optional[Reranker],
        **kwargs,
    ):
        """
        Initialize the CompositeRetriever.

        Parameters
        ----------
        retrievers : list[RetrieverQuark]
            A list of retriever quarks to be used by the composite retriever.
        reranker : Optional[Reranker]
            An optional reranker to rerank the retrieved results.
        **kwargs : dict
            Additional keyword arguments to be passed to the superclass initializer.
        """
        super().__init__(**kwargs)
        self._reranker = reranker
        self._retrievers = retrievers

    def verify_readiness(self) -> None:
        """
        Verify the readiness of the retrievers.

        This method checks if the vector database contains a non-empty collection
        with the expected name by invoking the `verify_readiness` method on each
        retriever in the `_retrievers` list.

        Raises
        ------
        Exception
            If any retriever's `verify_readiness` method raises an exception.
        """
        for retriever in self._retrievers:
            retriever.verify_readiness()

    async def ainvoke(
        self, retriever_input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list[Document]:
        """
        Asynchronously invokes the retrievers with the given input and configuration.

        Parameters
        ----------
        retriever_input : str
            The input string to be processed by the retrievers.
        config : Optional[RunnableConfig]
            Configuration for the retrievers (default None).
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        list[Document]
            A list of Document objects after processing by the retrievers and optional reranker.

        Notes
        -----
        - If no configuration is provided, a default configuration with empty metadata is used.
        - Summaries are removed from the results.
        - Duplicate entries are removed based on their metadata ID.
        - If a reranker is available, the results are further processed by the reranker.
        """
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

        if self._reranker and results:
            return_val = await self._reranker.ainvoke((return_val, retriever_input), config=config)

        return return_val
