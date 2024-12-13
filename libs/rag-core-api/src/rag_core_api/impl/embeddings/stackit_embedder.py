"""Module that contains the StackitEmbedder class."""

from langchain_core.embeddings import Embeddings
from openai import OpenAI

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings


class StackitEmbedder(Embedder, Embeddings):
    """
    A class that represents any Langchain provided Embedder.
    """

    def __init__(self, stackit_embedder_settings: StackitEmbedderSettings):
        """
        Initialize the StackitEmbedder with the given settings.

        Parameters
        ----------
        stackit_embedder_settings : StackitEmbedderSettings
            The settings for configuring the StackitEmbedder, including the API key and base URL.
        """
        self._client = OpenAI(
            api_key=stackit_embedder_settings.api_key,
            base_url=stackit_embedder_settings.base_url,
        )
        self._settings = stackit_embedder_settings

    def get_embedder(self) -> "StackitEmbedder":
        """
        Returns the embedder instance.

        Returns
        -------
        StackitEmbedder
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
        responses = self._client.embeddings.create(
            input=texts,
            model=self._settings.model,
        )

        return [data.embedding for data in responses.data]

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
        return self.embed_documents([text])[0]
