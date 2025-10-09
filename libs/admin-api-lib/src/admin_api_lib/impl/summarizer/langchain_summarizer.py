"""Module for the LangchainSummarizer class."""

import asyncio
import logging
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableConfig, ensure_config
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from admin_api_lib.impl.settings.summarizer_settings import SummarizerSettings
from admin_api_lib.summarizer.summarizer import (
    Summarizer,
    SummarizerInput,
    SummarizerOutput,
)
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore
from rag_core_lib.impl.utils.retry_decorator import create_retry_decorator_settings, retry_with_backoff

logger = logging.getLogger(__name__)


class LangchainSummarizer(Summarizer):
    """Is responsible for summarizing input data.

    LangchainSummarizer is responsible for summarizing input data using the LangfuseManager,
    RecursiveCharacterTextSplitter, and AsyncThreadsafeSemaphore. It handles chunking of the input
    document and retries the summarization process if an error occurs.
    """

    def __init__(
        self,
        langfuse_manager: LangfuseManager,
        chunker: RecursiveCharacterTextSplitter,
        semaphore: AsyncThreadsafeSemaphore,
        summarizer_settings: SummarizerSettings,
        retry_decorator_settings: RetryDecoratorSettings,
    ):
        self._chunker = chunker
        self._langfuse_manager = langfuse_manager
        self._semaphore = semaphore
        self._retry_decorator_settings = create_retry_decorator_settings(summarizer_settings, retry_decorator_settings)

    async def ainvoke(self, query: SummarizerInput, config: Optional[RunnableConfig] = None) -> SummarizerOutput:
        """
        Asynchronously invokes the summarization process on the given query.

        Parameters
        ----------
        query : SummarizerInput
            The input data to be summarized.
        config : Optional[RunnableConfig], optional
            Configuration options for the summarization process, by default None.

        Returns
        -------
        SummarizerOutput
            The summarized output.

        Raises
        ------
        Exception
            If the summary creation fails after the allowed number of tries.

        Notes
        -----
        This method handles chunking of the input document and retries the summarization
        process if an error occurs, up to the number of tries specified in the config.
        """
        assert query, "Query is empty: %s" % query  # noqa S101
        config = ensure_config(config)

        document = Document(page_content=query)
        langchain_documents = self._chunker.split_documents([document])
        logger.debug("Summarizing %d chunk(s)...", len(langchain_documents))

        # Fan out with concurrency, bounded by your semaphore inside _summarize_chunk
        tasks = [asyncio.create_task(self._summarize_chunk(doc.page_content, config)) for doc in langchain_documents]
        outputs = await asyncio.gather(*tasks)

        if len(outputs) == 1:
            return outputs[0]

        merged = " ".join(outputs)

        logger.debug(
            "Reduced number of chars from %d to %d",
            len("".join([x.page_content for x in langchain_documents])),
            len(merged),
        )
        return await self._summarize_chunk(merged, config)

    def _create_chain(self) -> Runnable:
        return self._langfuse_manager.get_base_prompt(self.__class__.__name__) | self._langfuse_manager.get_base_llm(
            self.__class__.__name__
        )

    def _retry_with_backoff_wrapper(self):
        return retry_with_backoff(
            settings=self._retry_decorator_settings,
            exceptions=(APIError, RateLimitError, APITimeoutError, APIConnectionError),
            rate_limit_exceptions=(RateLimitError,),
            logger=logger,
        )

    async def _summarize_chunk(self, text: str, config: Optional[RunnableConfig]) -> SummarizerOutput:
        @self._retry_with_backoff_wrapper()
        async def _call(text: str, config: Optional[RunnableConfig]) -> SummarizerOutput:
            response = await self._create_chain().ainvoke({"text": text}, config)
            return response.content if hasattr(response, "content") else str(response)

        # Hold the semaphore for the entire retry lifecycle
        async with self._semaphore:
            return await _call(text, config)
