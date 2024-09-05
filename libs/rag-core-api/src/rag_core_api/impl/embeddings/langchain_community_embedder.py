from langchain_core.embeddings import Embeddings

from rag_core_api.embeddings.embedder import Embedder


class LangchainCommunityEmbedder(Embedder, Embeddings):
    """
    A class that represents any Langchain provided Embedder.
    """

    def __init__(self, embedder: Embeddings):
        self._embedder = embedder

    def get_embedder(self):
        """
        Returns the embedder instance.

        Returns:
            The embedder instance.
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embedder.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embedder.embed_query(text)
