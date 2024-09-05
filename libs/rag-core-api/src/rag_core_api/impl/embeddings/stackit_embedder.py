from openai import OpenAI
from langchain_core.embeddings import Embeddings

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings


class StackitEmbedder(Embedder, Embeddings):
    """
    A class that represents any Langchain provided Embedder.
    """

    def __init__(self, stackit_embedder_settings: StackitEmbedderSettings):
        self._client = OpenAI(
            api_key=stackit_embedder_settings.api_key,
            base_url=stackit_embedder_settings.base_url,
        )
        self._settings = stackit_embedder_settings

    def get_embedder(self):
        """
        Returns the embedder instance.

        Returns:
            The embedder instance.
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        responses = self._client.embeddings.create(
            input=texts,
            model=self._settings.model,
        )

        return [data.embedding for data in responses.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
