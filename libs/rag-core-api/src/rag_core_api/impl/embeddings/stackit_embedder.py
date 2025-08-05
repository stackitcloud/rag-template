"""Module that contains the StackitEmbedder class."""

import time
import logging

from langchain_core.embeddings import Embeddings
from openai import OpenAI

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings

logger = logging.getLogger(__name__)


class StackitEmbedder(Embedder, Embeddings):
    """A class that represents any Langchain provided Embedder."""

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
        """Return the embedder instance.

        Returns
        -------
        StackitEmbedder
        """
        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of texts with exponential backoff retry logic. Batching is handled by the vector
        database client.

        Parameters
        ----------
        texts : list of str
            A batch of texts to be embedded.

        Returns
        -------
        list[list[float]]
            A list of embeddings for the batch.

        Raises
        ------
        Exception
            If all retry attempts fail.
        """
        if not texts:
            return []

        for attempt in range(self._settings.max_retries + 1):
            try:
                responses = self._client.embeddings.create(
                    input=texts,
                    model=self._settings.model,
                )
                return [data.embedding for data in responses.data]

            except Exception as e:
                if attempt == self._settings.max_retries:
                    logger.error("Failed to embed batch after %d attempts: %s",
                               self._settings.max_retries + 1, str(e))
                    raise

                # Calculate exponential backoff delay
                delay = min(
                    self._settings.retry_base_delay * (2 ** attempt),
                    self._settings.retry_max_delay
                )

                logger.warning("Embedding attempt %d/%d failed: %s. Retrying in %.2f seconds...",
                             attempt + 1, self._settings.max_retries + 1, str(e), delay)

                time.sleep(delay)

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
