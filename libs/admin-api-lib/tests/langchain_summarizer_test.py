import asyncio

import pytest
from langchain_core.documents import Document

from admin_api_lib.impl.settings.summarizer_settings import SummarizerSettings
from admin_api_lib.impl.summarizer.langchain_summarizer import LangchainSummarizer
from rag_core_lib.impl.settings.retry_decorator_settings import RetryDecoratorSettings
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore


class _StaticChunker:
    def __init__(self, docs: list[Document]):
        self._docs = docs

    def split_documents(self, _docs: list[Document]) -> list[Document]:
        return self._docs


class _ConcurrencyTrackingSummarizer(LangchainSummarizer):
    def __init__(self, docs: list[Document]):
        super().__init__(
            langfuse_manager=object(),  # type: ignore[arg-type]
            chunker=_StaticChunker(docs),  # type: ignore[arg-type]
            semaphore=AsyncThreadsafeSemaphore(100),
            summarizer_settings=SummarizerSettings(),
            retry_decorator_settings=RetryDecoratorSettings(),
        )
        self.in_flight = 0
        self.max_in_flight = 0

    async def _summarize_chunk(self, text: str, config):  # type: ignore[override]
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(0.01)
        self.in_flight -= 1
        return text


@pytest.mark.asyncio
async def test_langchain_summarizer_respects_max_concurrency_one():
    docs = [Document(page_content=f"chunk-{idx}") for idx in range(5)]
    summarizer = _ConcurrencyTrackingSummarizer(docs)

    await summarizer.ainvoke("input", config={"max_concurrency": 1})

    assert summarizer.max_in_flight == 1


@pytest.mark.asyncio
async def test_langchain_summarizer_respects_max_concurrency_limit():
    docs = [Document(page_content=f"chunk-{idx}") for idx in range(8)]
    summarizer = _ConcurrencyTrackingSummarizer(docs)

    await summarizer.ainvoke("input", config={"max_concurrency": 2})

    assert summarizer.max_in_flight <= 2

