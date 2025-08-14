"""Module that contains the StackitEmbedder class."""

import time
import logging
import random

from langchain_core.embeddings import Embeddings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, APIConnectionError
from fastapi import status

from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.impl.settings.stackit_embedder_settings import StackitEmbedderSettings

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

        for attempt in range(self._settings.max_retries + 1):
            response = None
            try:
                response = self._client.embeddings.with_raw_response.create(
                    input=texts,
                    model=self._settings.model,
                )
                # Success - return embeddings
                return [data.embedding for data in response.parse().data]

            except (APIError, RateLimitError, APITimeoutError, APIConnectionError) as e:
                # Prefer rate-limit-aware retry using headers when available
                resp = getattr(e, "response", None)
                status_code = getattr(resp, "status_code", None)
                raw_headers = getattr(resp, "headers", {}) or {}
                # Normalize header keys to lowercase for case-insensitive access
                headers = {str(k).lower(): v for k, v in raw_headers.items()} if isinstance(raw_headers, dict) else {}

                if isinstance(e, RateLimitError) or status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                    # Use Stackit AI Model Serving rate limit headers to determine wait
                    # x-ratelimit-reset-requests / x-ratelimit-reset-tokens can be like "1s" or "1.5s"
                    def _to_seconds(v):
                        if v is None:
                            return None
                        try:
                            # Accept numbers, "1", "1.5", "1s"
                            s = str(v).strip().lower()
                            if s.endswith("s"):
                                return float(s[:-1])
                            return float(s)
                        except Exception:
                            return None

                    wait_candidates = []
                    if headers:
                        request_reset = headers.get("x-ratelimit-reset-requests")
                        token_reset = headers.get("x-ratelimit-reset-tokens")
                        for v in (request_reset, token_reset):
                            fv = _to_seconds(v)
                            if fv is not None:
                                wait_candidates.append(fv)

                    # Fallback to exponential backoff if headers missing
                    wait = (
                        max(wait_candidates) if wait_candidates else min(
                            self._settings.retry_base_delay * (self.BACKOFF_FACTOR ** min(attempt, self.ATTEMPT_CAP)),
                            self._settings.retry_max_delay,
                        )
                    )
                    # Fixed jitter independent of wait to avoid thundering herd (50–250ms)
                    jitter = random.uniform(self.JITTER_MIN_SECONDS, self.JITTER_MAX_SECONDS)
                    total_wait = min(wait + jitter, self._settings.retry_max_delay)

                    logger.warning(
                        "Rate limited (429). Remaining: req=%s tok=%s. Reset in: req=%s tok=%s. Retrying in %.2fs (attempt %d/%d)...",
                        headers.get("x-ratelimit-remaining-requests", "?"),
                        headers.get("x-ratelimit-remaining-tokens", "?"),
                        headers.get("x-ratelimit-reset-requests", "?"),
                        headers.get("x-ratelimit-reset-tokens", "?"),
                        total_wait,
                        attempt + 1,
                        self._settings.max_retries + 1,
                    )
                    time.sleep(total_wait)
                    continue

                if attempt == self._settings.max_retries:
                    logger.error(
                        "Failed to embed batch after %d attempts: %s",
                        self._settings.max_retries + 1,
                        str(e),
                    )
                    raise

                # Exponential backoff for non-429 errors (timeouts, connections, etc.)
                delay = min(
                    self._settings.retry_base_delay * (self.BACKOFF_FACTOR ** min(attempt, self.ATTEMPT_CAP)),
                    self._settings.retry_max_delay,
                )

                logger.warning(
                    "Embedding attempt %d/%d failed: %s. Retrying in %.2f seconds...",
                    attempt + 1,
                    self._settings.max_retries + 1,
                    str(e),
                    delay,
                )

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
