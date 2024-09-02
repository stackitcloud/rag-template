from hashlib import sha256
from typing import Optional

from langchain_core.runnables import RunnableConfig
from tqdm import tqdm
from langchain_core.documents import Document
from rag_core_lib.impl.data_types.content_type import ContentType

from admin_backend.impl.information_enhancer.summary_enhancer import SummaryEnhancer


class SingleSummaryEnhancer(SummaryEnhancer):
    BASE64_IMAGE_KEY = "base64_image"

    def _create_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        summaries = []
        for info in tqdm(information):
            summary = self._summarizer.invoke(info.page_content, config)
            meta = {key: value for key, value in info.metadata.items() if key != self.BASE64_IMAGE_KEY}
            meta["id"] = sha256(str.encode(summary)).hexdigest()
            meta["related"].append(info.metadata["id"])
            meta["type"] = ContentType.SUMMARY.value
            summaries.append(Document(metadata=meta, page_content=summary))
        return summaries
