"""Module that contains the StackitEmbedder class."""

import logging

from langchain_core.embeddings import Embeddings
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError

from rag_core_lib.impl.embeddings.embedder import Embedder
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
from rag_core_lib.impl.utils.retry_decorator import (
    create_retry_decorator_settings,
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


class StackitEmbedder(Embedder, Embeddings):
    """LangChain-compatible embedder for STACKIT's OpenAI-compatible service."""

    def __init__(
        self,
        stackit_embedder_settings: StackitEmbedderSettings,
        retry_decorator_settings: RetryDecoratorSettings,
    ) -> None:
        """Initialise the Stackit embedder.

        Parameters
        ----------
        stackit_embedder_settings : StackitEmbedderSettings
            Configuration for the STACKIT embeddings endpoint.
        retry_decorator_settings : RetryDecoratorSettings
            Fallback retry configuration when the STACKIT-specific overrides are missing.
        """
        self._client = OpenAI(
            api_key=stackit_embedder_settings.api_key,
            base_url=stackit_embedder_settings.base_url,
        )
        self._settings = stackit_embedder_settings
        self._retry_decorator_settings = create_retry_decorator_settings(
            stackit_embedder_settings,
            retry_decorator_settings,
        )

    def get_embedder(self) -> "StackitEmbedder":
        """Return the embedder instance."""

        return self

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents using the STACKIT embeddings endpoint."""

        @self._retry_with_backoff_wrapper()
        def _call(documents: list[str]) -> list[list[float]]:
            responses = self._client.embeddings.create(
                input=documents,
                model=self._settings.model,
            )
            return [data.embedding for data in responses.data]

        return _call(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query using the STACKIT embeddings endpoint."""

        embeddings_list = self.embed_documents([text])
        if embeddings_list:
            embeddings = embeddings_list[0]
            return embeddings if embeddings else []
        logger.warning("No embeddings found for query: %s", text)
        return embeddings_list

    def _retry_with_backoff_wrapper(self):
        return retry_with_backoff(
            settings=self._retry_decorator_settings,
            exceptions=(APIError, RateLimitError, APITimeoutError, APIConnectionError),
            rate_limit_exceptions=(RateLimitError,),
            logger=logger,
        )
