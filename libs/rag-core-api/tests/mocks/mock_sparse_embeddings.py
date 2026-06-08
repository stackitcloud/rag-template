"""Provide deterministic sparse embeddings for tests."""

from langchain_qdrant import SparseEmbeddings
from langchain_qdrant.sparse_embeddings import SparseVector


class MockSparseEmbeddings(SparseEmbeddings):
    """Return a fixed sparse vector without loading an external model."""

    def embed_documents(self, texts: list[str]) -> list[SparseVector]:
        """Embed documents with a deterministic test vector."""
        return [SparseVector(indices=[0], values=[1.0]) for _ in texts]

    def embed_query(self, text: str) -> SparseVector:
        """Embed a query with a deterministic test vector."""
        return SparseVector(indices=[0], values=[1.0])
