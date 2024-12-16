"""Module that contains the AlephAlphaEmbedder class."""

from langchain_community.embeddings import AlephAlphaAsymmetricSemanticEmbedding
from langchain_core.embeddings import Embeddings

from rag_core_api.embeddings.embedder import Embedder
from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings
from rag_core_lib.secret_provider.secret_provider import SecretProvider


class AlephAlphaEmbedder(Embedder, Embeddings):
    """A class that represents an embedding model using AlephAlphaAsymmetricSemanticEmbedding.

    Creates embeddings for documents and queries using the AlephAlphaAsymmetricSemanticEmbedding model.
    """

    def __init__(
        self,
        settings: AlephAlphaSettings,
        secret_provider: SecretProvider,
        size: int = 128,
    ):
        """Initialize the AlephAlphaEmbedder with the given settings, secret provider, and size.

        Parameters
        ----------
        settings : AlephAlphaSettings
            The settings for the AlephAlphaEmbedder.
        secret_provider : SecretProvider
            The provider for secrets required by the embedder.
        size : int, optional
            The size of the embeddings (default 128).
        """
        self._secret_provider = secret_provider
        self._settings = settings
        self._size = size

    def get_embedder(self) -> "AlephAlphaEmbedder":
        """
        Return the embedder instance.

        Returns
        -------
        AlephAlphaEmbedder
            The embedder instance.
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of documents into numerical vectors.

        Parameters
        ----------
        texts : list of str
            A list of documents to be embedded.

        Returns
        -------
        list[list[float]]
            A list where each element is a list of floats representing the embedded vector of a document.
        """
        return self._create_embedder().embed_documents(texts)

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
        return self._create_embedder().embed_query(text)

    def _create_embedder(self):
        return AlephAlphaAsymmetricSemanticEmbedding(
            normalize=True,
            compress_to_size=self._size,
            aleph_alpha_api_key=self._secret_provider.provide_token()[self._secret_provider.provided_key],
            host=self._settings.host,
        )
