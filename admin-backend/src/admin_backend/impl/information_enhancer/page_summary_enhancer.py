from hashlib import sha256
from typing import Optional

from langchain_core.runnables import RunnableConfig
from tqdm import tqdm
from langchain_core.documents import Document
from rag_core_lib.impl.data_types.content_type import ContentType

from admin_backend.impl.information_enhancer.summary_enhancer import SummaryEnhancer


class PageSummaryEnhancer(SummaryEnhancer):
    BASE64_IMAGE_KEY = "base64_image"

    def _create_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        summaries = []

        # group infos by page
        grouped = [
            [info for info in information if info.metadata["page"] == page]
            for page in {info_piece.metadata["page"] for info_piece in information}
        ]

        for info_group in tqdm(grouped):
            summaries.append(self._summarize_page(info_group, config))
        return summaries

    def _summarize_page(self, page_pieces: list[Document], config: Optional[RunnableConfig]) -> Document:
        full_page_content = " ".join([piece.page_content for piece in page_pieces])
        summary = self._summarizer.invoke(full_page_content, config)
        meta = {key: value for key, value in page_pieces[0].metadata.items() if key != self.BASE64_IMAGE_KEY}
        meta["id"] = sha256(str.encode(full_page_content)).hexdigest()
        meta["related"] = meta["related"] + [piece.metadata["id"] for piece in page_pieces]
        meta["type"] = ContentType.SUMMARY.value

        return Document(metadata=meta, page_content=summary)
