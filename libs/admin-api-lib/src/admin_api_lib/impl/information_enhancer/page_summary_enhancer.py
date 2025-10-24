"""Module for enhancing the summary of pages by grouping information by page and summarizing each page."""

from asyncio import gather
from hashlib import sha256
from typing import Optional

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
    DEFAULT_PAGE_NR = 1

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
        distinct_pages = []
        for info in information:
            if info.metadata.get("page", self.DEFAULT_PAGE_NR) not in distinct_pages:
                distinct_pages.append(info.metadata.get("page", self.DEFAULT_PAGE_NR))

        grouped = []
        for page in distinct_pages:
            group = []
            for compare_info in information:
                if compare_info.metadata.get("page", self.DEFAULT_PAGE_NR) == page:
                    group.append(compare_info)
            if (
                self._chunker_settings
                and len(" ".join([item.page_content for item in group])) < self._chunker_settings.max_size
            ):
                continue
            grouped.append(group)

        summary_tasks = [self._asummarize_page(info_group, config) for info_group in tqdm(grouped)]

        return await gather(*summary_tasks)
