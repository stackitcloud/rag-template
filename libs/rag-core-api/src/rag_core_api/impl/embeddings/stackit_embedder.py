"""Module that contains the StackitEmbedder class."""

from langchain_core.embeddings import Embeddings
from openai import OpenAI, APIConnectionError, APIError, APITimeoutError, RateLimitError

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings
import logging
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.utils.retry_decorator import retry_with_backoff

logger = logging.getLogger(__name__)


class StackitEmbedder(Embedder, Embeddings):
    """A class that represents any Langchain provided Embedder."""

    def __init__(
        self, stackit_embedder_settings: StackitEmbedderSettings, retry_decorator_settings: RetryDecoratorSettings
    ):
        """
        Initialize the StackitEmbedder with the given settings.

        Parameters
        ----------
        stackit_embedder_settings : StackitEmbedderSettings
            The settings for configuring the StackitEmbedder, including the API key and base URL.
        retry_decorator_settings : RetryDecoratorSettings
            Default retry settings used as fallback when StackitEmbedderSettings leaves fields unset.
        """
        self._client = OpenAI(
            api_key=stackit_embedder_settings.api_key,
            base_url=stackit_embedder_settings.base_url,
        )
        self._settings = stackit_embedder_settings
        self._retry_decorator_settings = self._create_retry_decorator_settings(
            stackit_embedder_settings, retry_decorator_settings
        )

    def get_embedder(self) -> "StackitEmbedder":
        """Return the embedder instance.

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

        @self._retry_with_backoff_wrapper()
        def _call(texts: list[str]) -> list[list[float]]:
            responses = self._client.embeddings.create(
                input=texts,
                model=self._settings.model,
            )
            return [data.embedding for data in responses.data]

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
        embeddings_list = self.embed_documents([text])
        if embeddings_list:
            embeddings = embeddings_list[0]
            return embeddings if embeddings else []
        logger.warning("No embeddings found for query: %s", text)
        return embeddings_list

    def _create_retry_decorator_settings(
        self,
        stackit_settings: StackitEmbedderSettings,
        retry_defaults: RetryDecoratorSettings,
    ) -> RetryDecoratorSettings:
        # Prefer values from StackitEmbedderSettings when provided;
        # otherwise fall back to RetryDecoratorSettings defaults
        return RetryDecoratorSettings(
            max_retries=(
                stackit_settings.max_retries if stackit_settings.max_retries is not None else retry_defaults.max_retries
            ),
            retry_base_delay=(
                stackit_settings.retry_base_delay
                if stackit_settings.retry_base_delay is not None
                else retry_defaults.retry_base_delay
            ),
            retry_max_delay=(
                stackit_settings.retry_max_delay
                if stackit_settings.retry_max_delay is not None
                else retry_defaults.retry_max_delay
            ),
            backoff_factor=(
                stackit_settings.backoff_factor
                if stackit_settings.backoff_factor is not None
                else retry_defaults.backoff_factor
            ),
            attempt_cap=(
                stackit_settings.attempt_cap if stackit_settings.attempt_cap is not None else retry_defaults.attempt_cap
            ),
            jitter_min=(
                stackit_settings.jitter_min if stackit_settings.jitter_min is not None else retry_defaults.jitter_min
            ),
            jitter_max=(
                stackit_settings.jitter_max if stackit_settings.jitter_max is not None else retry_defaults.jitter_max
            ),
        )

    def _retry_with_backoff_wrapper(self):
        return retry_with_backoff(
            settings=self._retry_decorator_settings,
            exceptions=(APIError, RateLimitError, APITimeoutError, APIConnectionError),
            rate_limit_exceptions=(RateLimitError,),
            logger=logger,
        )
