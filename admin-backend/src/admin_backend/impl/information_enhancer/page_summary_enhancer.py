from asyncio import gather
from hashlib import sha256
from typing import Optional

from langchain_core.runnables import RunnableConfig
from tqdm import tqdm
from langchain_core.documents import Document
from rag_core_lib.impl.data_types.content_type import ContentType

from admin_backend.impl.information_enhancer.summary_enhancer import SummaryEnhancer


class PageSummaryEnhancer(SummaryEnhancer):
    BASE64_IMAGE_KEY = "base64_image"

    async def _acreate_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        # group infos by page
        grouped = [
            [info for info in information if info.metadata["page"] == page]
            for page in {info_piece.metadata["page"] for info_piece in information}
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
