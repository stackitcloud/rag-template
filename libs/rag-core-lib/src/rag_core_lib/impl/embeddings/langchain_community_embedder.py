"""Module that contains the LangchainCommunityEmbedder class."""

from langchain_core.embeddings import Embeddings

from rag_core_lib.impl.embeddings.embedder import Embedder


class LangchainCommunityEmbedder(Embedder, Embeddings):
    """A wrapper around any LangChain-provided embedder."""

    def __init__(self, embedder: Embeddings):
        """Initialise the wrapper with the provided embedder.

        Parameters
        ----------
        embedder : Embeddings
            The embedder instance to delegate to.
        """
        self._embedder = embedder

    def get_embedder(self) -> "LangchainCommunityEmbedder":
        """Return the embedder instance."""

        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents using the wrapped embedder."""

        return self._embedder.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query using the wrapped embedder."""

        return self._embedder.embed_query(text)
