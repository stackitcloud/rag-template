"""Mock implementation of a minimal vector database interface for tests.

Provides only the methods required by the CompositeRetriever unit tests:
- get_documents_by_ids: Used during summary expansion
- asearch: (async) provided as a defensive stub
"""
from typing import Dict, List
from langchain_core.documents import Document

__all__ = ["MockVectorDB"]


class MockVectorDB:
    def __init__(self, docs_by_id: Dict[str, Document] | None = None):
        self.collection_available = True
        self._docs_by_id = docs_by_id or {}

    def get_documents_by_ids(self, ids: List[str]) -> List[Document]:  # pragma: no cover - simple mapping
        return [self._docs_by_id[i] for i in ids if i in self._docs_by_id]

    async def asearch(self, *_, **__):  # pragma: no cover - defensive stub
        return []
