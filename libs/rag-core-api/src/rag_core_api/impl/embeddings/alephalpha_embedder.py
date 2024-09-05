from langchain_community.embeddings import AlephAlphaAsymmetricSemanticEmbedding
from langchain_core.embeddings import Embeddings

from rag_core_lib.secret_provider.secret_provider import SecretProvider
from rag_core_lib.impl.settings.aleph_alpha_settings import AlephAlphaSettings

from rag_core_api.embeddings.embedder import Embedder


class AlephAlphaEmbedder(Embedder, Embeddings):
    """
    A class that represents an embedding model using AlephAlphaAsymmetricSemanticEmbedding.

    Args:
        size (int): The size of the embedding vectors. Defaults to 128.

    Attributes:
        _embedder: An instance of AlephAlphaAsymmetricSemanticEmbedding.
    """

    def __init__(
        self,
        settings: AlephAlphaSettings,
        secret_provider: SecretProvider,
        size: int = 128,
    ):
        self._secret_provider = secret_provider
        self._settings = settings
        self._size = size

    def get_embedder(self):
        """
        Returns the embedder instance.

        Returns:
            The embedder instance.
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._create_embedder().embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._create_embedder().embed_query(text)

    def _create_embedder(self):
        return AlephAlphaAsymmetricSemanticEmbedding(
            normalize=True,
            compress_to_size=self._size,
            aleph_alpha_api_key=self._secret_provider.provide_token()[self._secret_provider.provided_key],
            host=self._settings.host,
        )
