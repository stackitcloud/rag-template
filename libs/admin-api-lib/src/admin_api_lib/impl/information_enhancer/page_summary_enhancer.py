"""Module for enhancing the summary of pages by grouping information by page and summarizing each page."""

from asyncio import gather
from hashlib import sha256
from typing import Optional
from typing import Any

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from tqdm import tqdm

from admin_api_lib.impl.information_enhancer.summary_enhancer import SummaryEnhancer
from rag_core_lib.impl.data_types.content_type import ContentType


class PageSummaryEnhancer(SummaryEnhancer):
    """
    Enhances the summary of pages by grouping information by page and summarizing each page.

    Attributes
    ----------
    BASE64_IMAGE_KEY : str
        Key used to identify base64 encoded images in metadata.
    DEFAULT_PAGE_NR : int
        Default page number used when no page metadata is available.
    """

    BASE64_IMAGE_KEY = "base64_image"
    DOCUMENT_URL_KEY = "document_url"
    DEFAULT_PAGE_NR = 1

    def _group_key(self, piece: Document) -> tuple[Any, ...]:
        document_url = piece.metadata.get(self.DOCUMENT_URL_KEY)
        page = piece.metadata.get("page", self.DEFAULT_PAGE_NR)

        # For paged documents (PDF/docling/etc.) keep per-page summaries even if a shared document URL exists.
        if isinstance(page, int):
            return ("page_number", document_url, page)

        # For sources like sitemaps/confluence, `page` can be a non-unique title (or missing),
        # so group by the page URL when available to ensure one summary per page.
        if document_url:
            return ("document_url", document_url)

        return ("page", page)

    async def _asummarize_page(self, page_pieces: list[Document], config: Optional[RunnableConfig]) -> Document:
        full_page_content = " ".join([piece.page_content for piece in page_pieces])
        summary = await self._summarizer.ainvoke(full_page_content, config)
        meta = {key: value for key, value in page_pieces[0].metadata.items() if key != self.BASE64_IMAGE_KEY}
        meta["id"] = sha256(str.encode(full_page_content)).hexdigest()
        meta["related"] = meta["related"] + [piece.metadata["id"] for piece in page_pieces]
        meta["related"] = list(set(meta["related"]))
        meta["type"] = ContentType.SUMMARY.value

        return Document(metadata=meta, page_content=summary)

    async def _acreate_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        ordered_keys: list[tuple[Any, ...]] = []
        groups: dict[tuple[Any, ...], list[Document]] = {}
        for info in information:
            key = self._group_key(info)
            if key not in groups:
                ordered_keys.append(key)
                groups[key] = []
            groups[key].append(info)

        grouped = [groups[key] for key in ordered_keys]
        summary_tasks = [self._asummarize_page(info_group, config) for info_group in tqdm(grouped)]

        return await gather(*summary_tasks)
