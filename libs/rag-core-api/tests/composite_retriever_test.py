"""Test internal helper methods of ``CompositeRetriever``.

The goal of these tests is to verify the transformation semantics of:
 - _use_summaries
 - _remove_duplicates
 - _early_pruning
 - _arerank_pruning

They operate with light‑weight mock objects (no real vector DB / reranker logic).
"""

from __future__ import annotations

import asyncio
from typing import Iterable

import pytest
from langchain_core.documents import Document

from rag_core_api.impl.retriever.composite_retriever import CompositeRetriever
from rag_core_lib.impl.data_types.content_type import ContentType
from mocks.mock_vector_db import MockVectorDB
from mocks.mock_retriever_quark import MockRetrieverQuark
from mocks.mock_reranker import MockReranker


def _mk_doc(
    doc_id: str,
    score: float | None = None,
    doc_type: ContentType = ContentType.TEXT,
    related: Iterable[str] | None = None,
):
    meta = {"id": doc_id, "type": doc_type.value}
    if score is not None:
        meta["score"] = score
    if related is not None:
        meta["related"] = list(related)
    return Document(page_content=f"content-{doc_id}", metadata=meta)


@pytest.mark.asyncio
async def test_use_summaries_expands_and_removes_summary():
    """Expand a summary into its related documents.

    Verify that summary documents are removed and replaced by their related underlying documents.
    """
    # Summary references an underlying doc not in initial results.
    underlying = _mk_doc("doc1", score=0.9)
    summary = _mk_doc("sum1", doc_type=ContentType.SUMMARY, related=["doc1"])  # type: ignore[arg-type]
    vector_db = MockVectorDB({"doc1": underlying})
    retriever = MockRetrieverQuark([summary, underlying], vector_database=vector_db)

    cr = CompositeRetriever(retrievers=[retriever], reranker=None, reranker_enabled=False)
    # Directly call _use_summaries for deterministic control
    results = cr._use_summaries([summary], [summary])

    # Underlying doc added (via expansion) & summary removed.
    assert len(results) == 1
    assert results[0].metadata["id"] == "doc1"
    assert all(d.metadata.get("type") != ContentType.SUMMARY.value for d in results)


def test_use_summaries_only_summary_no_related():
    """Drop a summary document that has no related documents.

    Verify that the returned result is empty when no related ids are present.
    """
    summary = _mk_doc("sum1", doc_type=ContentType.SUMMARY, related=[])  # type: ignore[arg-type]
    retriever = MockRetrieverQuark([summary])
    cr = CompositeRetriever(retrievers=[retriever], reranker=None, reranker_enabled=False)
    results = cr._use_summaries([summary], [summary])
    # Expect empty list after removal because there are no related expansions.
    assert results == []


def test_remove_duplicates_preserves_first_occurrence():
    """Preserve the first occurrence when duplicate ids are present.

    Verify that duplicate documents are removed while maintaining the original order.
    """
    d1a = _mk_doc("a")
    d1b = _mk_doc("a")  # duplicate id
    d2 = _mk_doc("b")
    retriever = MockRetrieverQuark([d1a, d1b, d2])
    cr = CompositeRetriever(retrievers=[retriever], reranker=None, reranker_enabled=False)
    unique = cr._remove_duplicates([d1a, d1b, d2])
    assert [d.metadata["id"] for d in unique] == ["a", "b"]


def test_early_pruning_sorts_by_score_when_all_have_score():
    """Sort by score and keep only the top-k documents.

    Verify that documents are sorted descending by score when all documents include scores.
    """
    docs = [_mk_doc("a", score=0.7), _mk_doc("b", score=0.9), _mk_doc("c", score=0.8)]
    retriever = MockRetrieverQuark(docs)
    cr = CompositeRetriever(
        retrievers=[retriever], reranker=None, reranker_enabled=False, total_retrieved_k_documents=2
    )
    pruned = cr._early_pruning(docs.copy())
    # Expect top two by score descending: b (0.9), c (0.8)
    assert [d.metadata["id"] for d in pruned] == ["b", "c"]


def test_early_pruning_preserves_order_without_scores():
    """Preserve input order when pruning without score metadata.

    Verify that pruning keeps the original order when scores are absent.
    """
    docs = [_mk_doc("a"), _mk_doc("b"), _mk_doc("c")]  # no scores
    retriever = MockRetrieverQuark(docs)
    cr = CompositeRetriever(
        retrievers=[retriever], reranker=None, reranker_enabled=False, total_retrieved_k_documents=2
    )
    pruned = cr._early_pruning(docs.copy())
    assert [d.metadata["id"] for d in pruned] == ["a", "b"]


@pytest.mark.asyncio
async def test_arerank_pruning_invokes_reranker_when_needed():
    """Invoke the reranker when more than k documents are retrieved.

    Verify that the reranker is called and that the returned list is trimmed to ``reranker_k_documents``.
    """
    docs = [_mk_doc("a", score=0.5), _mk_doc("b", score=0.7), _mk_doc("c", score=0.9)]
    retriever = MockRetrieverQuark(docs)
    reranker = MockReranker()
    cr = CompositeRetriever(
        retrievers=[retriever],
        reranker=reranker,
        reranker_enabled=True,
        reranker_k_documents=2,
    )
    pruned = await cr._arerank_pruning(docs.copy(), retriever_input="question")
    # Reranker should be invoked and return top-2 by score (ids c, b)
    assert reranker.invoked is True
    assert [d.metadata["id"] for d in pruned] == ["c", "b"]
    assert len(pruned) == 2


@pytest.mark.asyncio
async def test_arerank_pruning_skips_when_not_needed():
    """Skip reranking when the retrieved docs are already within k.

    Verify that the reranker is not invoked when no pruning is required.
    """
    docs = [_mk_doc("a", score=0.5), _mk_doc("b", score=0.7)]  # already <= k
    retriever = MockRetrieverQuark(docs)
    reranker = MockReranker()
    cr = CompositeRetriever(
        retrievers=[retriever],
        reranker=reranker,
        reranker_enabled=True,
        reranker_k_documents=3,
    )
    pruned = await cr._arerank_pruning(docs.copy(), retriever_input="question")
    # Not invoked because len(docs) <= reranker_k_documents
    assert reranker.invoked is False
    assert pruned == docs


# Convenience: allow running this test module directly for quick local dev.
if __name__ == "__main__":  # pragma: no cover
    asyncio.run(pytest.main([__file__]))
