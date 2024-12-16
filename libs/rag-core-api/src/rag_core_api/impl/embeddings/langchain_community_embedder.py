"""Module that contains the LangchainCommunityEmbedder class."""

from langchain_core.embeddings import Embeddings

from rag_core_api.embeddings.embedder import Embedder


class LangchainCommunityEmbedder(Embedder, Embeddings):
    """A class that represents any Langchain provided Embedder."""

    def __init__(self, embedder: Embeddings):
        """Initialize the LangchainCommunityEmbedder with the given embedder.

        Parameters
        ----------
        embedder : Embeddings
            An instance of the Embeddings class used for embedding operations.
        """
        self._embedder = embedder

    def get_embedder(self) -> "LangchainCommunityEmbedder":
        """Return the embedder instance.

        Returns
        -------
        LangchainCommunityEmbedder
            The embedder instance.
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents into numerical vectors.

        Parameters
        ----------
        texts : list[str]
            A list of documents to be embedded.

        Returns
        -------
        list[list[float]]
            A list where each element is a list of floats representing the embedded vector of a document.
        """
        return self._embedder.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a given query text into a list of float values.

        Parameters
        ----------
        text : str
            The query text to be embedded.

        Returns
        -------
        list[float]
            The embedded representation of the query text.
        """
        return self._embedder.embed_query(text)
