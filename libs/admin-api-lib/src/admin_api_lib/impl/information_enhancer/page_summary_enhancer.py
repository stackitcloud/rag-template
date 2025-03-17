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

    async def _acreate_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        # group infos by page, defaulting to page 1 if no page metadata
        if self._chunker_settings:
            filtered_information = [
                info for info in information if len(info.page_content) > self._chunker_settings.max_size
            ]
        else:
            filtered_information = information
        grouped = [
            [info for info in filtered_information if info.metadata.get("page", self.DEFAULT_PAGE_NR) == page]
            for page in {info_piece.metadata.get("page", self.DEFAULT_PAGE_NR) for info_piece in filtered_information}
        ]

        summary_tasks = [self._asummarize_page(info_group, config) for info_group in tqdm(grouped)]
        return await gather(*summary_tasks)

    async def _asummarize_page(self, page_pieces: list[Document], config: Optional[RunnableConfig]) -> Document:
        full_page_content = " ".join([piece.page_content for piece in page_pieces])
        summary = await self._summarizer.ainvoke(full_page_content, config)
        meta = {key: value for key, value in page_pieces[0].metadata.items() if key != self.BASE64_IMAGE_KEY}
        meta["id"] = sha256(str.encode(full_page_content)).hexdigest()
        meta["related"] = meta["related"] + [piece.metadata["id"] for piece in page_pieces]
        meta["type"] = ContentType.SUMMARY.value

        return Document(metadata=meta, page_content=summary)
