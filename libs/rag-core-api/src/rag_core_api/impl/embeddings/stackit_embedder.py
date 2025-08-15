"""Module that contains the StackitEmbedder class."""

import logging

from langchain_core.embeddings import Embeddings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, APIConnectionError

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
from rag_core_lib.impl.utils.retry_decorator import RetrySettings, retry_with_backoff


logger = logging.getLogger(__name__)


class StackitEmbedder(Embedder, Embeddings):
    """A class that represents any Langchain provided Embedder."""

    ATTEMPT_CAP = 10
    BACKOFF_FACTOR = 2
    JITTER_MIN_SECONDS = 0.05
    JITTER_MAX_SECONDS = 0.25

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
        texts : list[str]
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

        @self._retry_wrapper()
        def _call(batch: list[str]) -> list[list[float]]:
            response = self._client.embeddings.with_raw_response.create(
                input=batch,
                model=self._settings.model,
            )
            return [data.embedding for data in response.parse().data]

        return _call(texts)

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
        embeddings = self.embed_documents([text])[0]
        return embeddings if embeddings else []

    def _retry_wrapper(self):
        """Build a retry decorator *with runtime settings* from self._settings."""
        return retry_with_backoff(
            settings=RetrySettings(
                max_retries=self._settings.max_retries,
                retry_base_delay=self._settings.retry_base_delay,
                retry_max_delay=self._settings.retry_max_delay,
                backoff_factor=self.BACKOFF_FACTOR,
                attempt_cap=self.ATTEMPT_CAP,
                jitter_min=self.JITTER_MIN_SECONDS,
                jitter_max=self.JITTER_MAX_SECONDS,
            ),
            exceptions=(APIError, RateLimitError, APITimeoutError, APIConnectionError),
            rate_limit_exceptions=(RateLimitError,),
            logger=logger,
        )

