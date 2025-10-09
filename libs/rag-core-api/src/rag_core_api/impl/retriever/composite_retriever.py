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
from typing import Any, Optional, Iterable

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
        reranker_enabled: bool,
        total_retrieved_k_documents: int | None = None,
        reranker_k_documents: int | None = None,
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
        reranker_enabled : bool
            A flag indicating whether the reranker is enabled.
        total_retrieved_k_documents : int | None
            The total number of documents to retrieve (default None, meaning no limit).
        reranker_k_documents : int | None
            The number of documents to retrieve for the reranker (default None, meaning no limit).
        **kwargs : dict
            Additional keyword arguments to be passed to the superclass initializer.
        """
        super().__init__(**kwargs)
        self._reranker = reranker
        self._retrievers = retrievers
        # Optional global cap (before reranking) on merged candidates. If None, no cap applied.
        self._total_retrieved_k_documents = total_retrieved_k_documents
        self._reranker_k_documents = reranker_k_documents
        self._reranker_enabled = reranker_enabled

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
            Configuration for the retrievers and reranker (default None).
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

        summary_docs: list[Document] = [d for d in results if d.metadata.get("type") == ContentType.SUMMARY.value]

        results = self._use_summaries(summary_docs, results)

        return_val = self._remove_duplicates(results)

        return_val = self._early_pruning(return_val)

        return_val = await self._arerank_pruning(return_val, retriever_input, config)

        return return_val

    def _use_summaries(self, summary_docs: list[Document], results: list[Document]) -> list[Document]:
        """Utilize summary documents to enhance retrieval results.

        Parameters
        ----------
        summary_docs : list[Document]
            A list of summary documents to use.
        results : list[Document]
            A list of retrieval results to enhance.

        Returns
        -------
        list[Document]
            The enhanced list of documents.
        """
        try:
            # Collect existing ids for fast membership tests
            existing_ids: set[str] = {d.metadata.get("id") for d in results}

            # Gather related ids not yet present

            missing_related_ids: set[str] = set()
            for sdoc in summary_docs:
                related_list: Iterable[str] = sdoc.metadata.get("related", [])
                for rid in related_list:
                    if rid and rid not in existing_ids:
                        missing_related_ids.add(rid)

            if missing_related_ids:
                # Heuristic: use the first retriever's underlying vector database for lookup.
                # All quarks share the same vector database instance in current design.
                vector_db = None
                if self._retrievers:
                    # Access protected member as an implementation detail – acceptable within package.
                    vector_db = getattr(self._retrievers[0], "_vector_database", None)
                if vector_db and hasattr(vector_db, "get_documents_by_ids"):
                    try:
                        expanded_docs: list[Document] = vector_db.get_documents_by_ids(list(missing_related_ids))
                        # Merge while preserving original order precedence (append new ones)
                        results.extend(expanded_docs)
                        existing_ids.update(d.metadata.get("id") for d in expanded_docs)
                        logger.debug(
                            "Summary expansion added %d underlying documents (from %d summaries).",
                            len(expanded_docs),
                            len(summary_docs),
                        )
                    except Exception:
                        logger.exception("Failed to expand summary related documents.")
                else:
                    logger.debug("Vector database does not expose get_documents_by_ids; skipping summary expansion.")
        finally:
            # Remove summaries after expansion step
            results = [x for x in results if x.metadata.get("type") != ContentType.SUMMARY.value]
        return results

    def _remove_duplicates(self, documents: list[Document]) -> list[Document]:
        """Remove duplicate documents from a list based on their IDs.

        Parameters
        ----------
        documents : list[Document]
            The list of documents to filter.

        Returns
        -------
        list[Document]
            The filtered list of documents with duplicates removed.
        """
        seen_ids = set()
        unique_docs = []
        for doc in documents:
            doc_id = doc.metadata.get("id")
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_docs.append(doc)
        return unique_docs

    def _early_pruning(self, documents: list[Document]) -> list[Document]:
        """Prune documents early based on certain criteria.

        Parameters
        ----------
        documents : list[Document]
            The list of documents to prune.

        Returns
        -------
        list[Document]
            The pruned list of documents.
        """
        # Optional early global pruning (only if configured and more than total_k)
        if self._total_retrieved_k_documents is not None and len(documents) > self._total_retrieved_k_documents:
            # If score metadata exists, use it to prune; otherwise keep ordering as-is.
            if all("score" in d.metadata for d in documents):
                documents.sort(key=lambda d: d.metadata["score"], reverse=True)
            documents = documents[: self._total_retrieved_k_documents]
        return documents

    async def _arerank_pruning(self, documents: list[Document], retriever_input: dict, config: Optional[RunnableConfig] = None) -> list[Document]:
        """Prune documents by reranker.

        Parameters
        ----------
        documents : list[Document]
            The list of documents to prune.
        retriever_input : dict
            The input to the retriever.
        config : Optional[RunnableConfig]
            Configuration for the retrievers and reranker (default None).

        Returns
        -------
        list[Document]
            The pruned list of documents.
        """
        if self._reranker_k_documents is not None and len(documents) > self._reranker_k_documents and self._reranker_enabled:
            # Only invoke reranker if there are more docs than it will output OR if score missing.
            try:
                documents = await self._reranker.ainvoke((documents, retriever_input), config=config)
            except Exception:  # pragma: no cover - fail soft; return unreranked if reranker errors
                logger.exception("Reranker failed; returning unreranked results.")
        return documents
