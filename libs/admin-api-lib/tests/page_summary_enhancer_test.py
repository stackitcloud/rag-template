import asyncio
from unittest.mock import AsyncMock

import pytest
from langchain_core.documents import Document

from admin_api_lib.impl.information_enhancer.page_summary_enhancer import PageSummaryEnhancer
from rag_core_lib.impl.data_types.content_type import ContentType


@pytest.mark.asyncio
async def test_page_summary_enhancer_groups_by_document_url_for_non_numeric_pages():
    summarizer = AsyncMock()
    summarizer.ainvoke = AsyncMock(return_value="summary")
    enhancer = PageSummaryEnhancer(summarizer)

    docs = [
        Document(
            page_content="page-a chunk-1",
            metadata={
                "id": "a1",
                "related": [],
                "type": ContentType.TEXT.value,
                "page": "Unknown Title",
                "document_url": "https://example.com/a",
            },
        ),
        Document(
            page_content="page-a chunk-2",
            metadata={
                "id": "a2",
                "related": [],
                "type": ContentType.TEXT.value,
                "page": "Unknown Title",
                "document_url": "https://example.com/a",
            },
        ),
        Document(
            page_content="page-b chunk-1",
            metadata={
                "id": "b1",
                "related": [],
                "type": ContentType.TEXT.value,
                "page": "Unknown Title",
                "document_url": "https://example.com/b",
            },
        ),
    ]

    summaries = await enhancer.ainvoke(docs)

    assert summarizer.ainvoke.call_count == 2
    assert len(summaries) == 2

    assert summaries[0].metadata["document_url"] == "https://example.com/a"
    assert set(summaries[0].metadata["related"]) == {"a1", "a2"}
    assert summaries[0].metadata["type"] == ContentType.SUMMARY.value

    assert summaries[1].metadata["document_url"] == "https://example.com/b"
    assert set(summaries[1].metadata["related"]) == {"b1"}
    assert summaries[1].metadata["type"] == ContentType.SUMMARY.value


@pytest.mark.asyncio
async def test_page_summary_enhancer_keeps_page_number_separation_for_paged_documents():
    summarizer = AsyncMock()
    summarizer.ainvoke = AsyncMock(return_value="summary")
    enhancer = PageSummaryEnhancer(summarizer)

    docs = [
        Document(
            page_content="page-1 chunk",
            metadata={
                "id": "p1",
                "related": [],
                "type": ContentType.TEXT.value,
                "page": 1,
                "document_url": "http://file.local/doc.pdf",
            },
        ),
        Document(
            page_content="page-2 chunk",
            metadata={
                "id": "p2",
                "related": [],
                "type": ContentType.TEXT.value,
                "page": 2,
                "document_url": "http://file.local/doc.pdf",
            },
        ),
    ]

    summaries = await enhancer.ainvoke(docs)

    assert summarizer.ainvoke.call_count == 2
    assert len(summaries) == 2
    assert set(summaries[0].metadata["related"]) == {"p1"}
    assert set(summaries[1].metadata["related"]) == {"p2"}


class _ConcurrencyTrackingSummarizer:
    def __init__(self) -> None:
        self.in_flight = 0
        self.max_in_flight = 0

    async def ainvoke(self, _query: str, _config=None) -> str:  # noqa: ANN001
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(0.01)
        self.in_flight -= 1
        return "summary"


@pytest.mark.asyncio
async def test_page_summary_enhancer_respects_max_concurrency_one():
    summarizer = _ConcurrencyTrackingSummarizer()
    enhancer = PageSummaryEnhancer(summarizer)  # type: ignore[arg-type]

    docs = [
        Document(page_content="page-a chunk", metadata={"id": "a1", "related": [], "type": ContentType.TEXT.value, "page": "A", "document_url": "https://example.com/a"}),
        Document(page_content="page-b chunk", metadata={"id": "b1", "related": [], "type": ContentType.TEXT.value, "page": "B", "document_url": "https://example.com/b"}),
        Document(page_content="page-c chunk", metadata={"id": "c1", "related": [], "type": ContentType.TEXT.value, "page": "C", "document_url": "https://example.com/c"}),
    ]

    await enhancer.ainvoke(docs, config={"max_concurrency": 1})

    assert summarizer.max_in_flight == 1
