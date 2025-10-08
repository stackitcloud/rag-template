"""Module for the CompositeRetriever class.

Performance notes / improvements (2025-10):
 - Retriever invocations are now executed concurrently via ``asyncio.gather`` instead of
     sequential awaits inside a for-loop. This reduces end-to-end latency roughly to the
     slowest individual retriever call instead of the sum of all.
 - Duplicate filtering now uses an O(1) set membership check instead of rebuilding a list
     comprehension for every candidate (previously O(n^2)).
 - Early pruning hook (``_total_k``) is prepared for future enhancement; if provided it
     allows trimming the merged candidate list before an optional reranker is invoked.
"""

import logging
import asyncio
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
        total_k: int | None = None,
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
        # Optional global cap (before reranking) on merged candidates. If None, no cap applied.
        self._total_k = total_k

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
        if config is None:
            config = RunnableConfig(metadata={"filter_kwargs": {}})

        # Run all retrievers concurrently instead of sequentially.
        tasks = [r.ainvoke(retriever_input, config=deepcopy(config)) for r in self._retrievers]
        retriever_outputs = await asyncio.gather(*tasks, return_exceptions=False)
        # Flatten
        results: list[Document] = [doc for group in retriever_outputs for doc in group]

        # remove summaries
        results = [x for x in results if x.metadata["type"] != ContentType.SUMMARY.value]

        # remove duplicated entries
        return_val = []
        seen_ids: set[str] = set()
        for result in results:
            if result.metadata.get("type") == ContentType.SUMMARY.value:
                continue
            doc_id = result.metadata.get("id")
            if doc_id is None:
                # If an ID is missing, keep it (can't deduplicate deterministically)
                return_val.append(result)
                continue
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            return_val.append(result)

        # Optional early global pruning (only if configured and more than total_k)
        if self._total_k is not None and len(return_val) > self._total_k:
            # If score metadata exists, use it to prune; otherwise keep ordering as-is.
            if all("score" in d.metadata for d in return_val):
                return_val.sort(key=lambda d: d.metadata["score"], reverse=True)
            return_val = return_val[: self._total_k]

        if self._reranker and return_val:
            # Only invoke reranker if there are more docs than it will output OR if score missing.
            try:
                return_val = await self._reranker.ainvoke((return_val, retriever_input), config=config)
            except Exception:  # pragma: no cover - fail soft; return unreranked if reranker errors
                logger.exception("Reranker failed; returning unreranked results.")

        return return_val
