"""Mock retriever quark for CompositeRetriever unit tests."""
from typing import List
from langchain_core.documents import Document

from .mock_vector_db import MockVectorDB

__all__ = ["MockRetrieverQuark"]


class MockRetrieverQuark:
    """Minimal stand-in for a RetrieverQuark.

    Exposes an ``ainvoke`` returning pre-seeded documents and a ``_vector_database`` attribute
    referenced by summary expansion logic.
    """

    def __init__(self, documents: List[Document], vector_database: MockVectorDB | None = None):
        self._documents = documents
        self._vector_database = vector_database or MockVectorDB()

    def verify_readiness(self):  # pragma: no cover - trivial
        return None

    async def ainvoke(self, *_args, **_kwargs):  # noqa: D401 - simple passthrough
        return self._documents
