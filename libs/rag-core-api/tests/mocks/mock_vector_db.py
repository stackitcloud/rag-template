"""Provide a minimal vector database interface for tests.

Provides only the methods required by the CompositeRetriever unit tests:
- get_documents_by_ids: Used during summary expansion
- asearch: (async) provided as a defensive stub
"""

from langchain_core.documents import Document

__all__ = ["MockVectorDB"]


class MockVectorDB:
    """Provide a minimal in-memory vector database test double."""

    def __init__(self, docs_by_id: dict[str, Document] | None = None):
        self.collection_available = True
        self._docs_by_id = docs_by_id or {}

    def get_documents_by_ids(self, ids: list[str]) -> list[Document]:  # pragma: no cover - simple mapping
        """Return documents for the provided ids.

        Parameters
        ----------
        ids : list[str]
            Document ids to look up.

        Returns
        -------
        list[Document]
            Documents that exist in the in-memory mapping.
        """
        return [self._docs_by_id[i] for i in ids if i in self._docs_by_id]

    async def asearch(self, *_, **__):  # pragma: no cover - defensive stub
        """Return an empty result for async search.

        Returns
        -------
        list
            Always returns an empty list.
        """
        return []
