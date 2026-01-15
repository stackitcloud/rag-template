"""Provide a mock retriever quark for CompositeRetriever unit tests."""

from langchain_core.documents import Document

from .mock_vector_db import MockVectorDB

__all__ = ["MockRetrieverQuark"]


class MockRetrieverQuark:
    """Provide a minimal stand-in for a RetrieverQuark.

    Exposes an ``ainvoke`` returning pre-seeded documents and a ``_vector_database`` attribute
    referenced by summary expansion logic.
    """

    def __init__(self, documents: list[Document], vector_database: MockVectorDB | None = None):
        self._documents = documents
        self._vector_database = vector_database or MockVectorDB()

    def verify_readiness(self):  # pragma: no cover - trivial
        """Verify that the retriever is ready.

        Returns
        -------
        None
            Always returns ``None``.
        """

    async def ainvoke(self, *_args, **_kwargs):
        """Return the pre-seeded documents.

        Returns
        -------
        list[Document]
            The documents passed to the constructor.
        """
        return self._documents
