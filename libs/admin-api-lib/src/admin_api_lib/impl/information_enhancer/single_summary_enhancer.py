from asyncio import gather
from hashlib import sha256
from typing import Optional

from langchain_core.runnables import RunnableConfig
from tqdm import tqdm
from langchain_core.documents import Document
from rag_core_lib.impl.data_types.content_type import ContentType

from admin_api_lib.impl.information_enhancer.summary_enhancer import SummaryEnhancer


class SingleSummaryEnhancer(SummaryEnhancer):
    BASE64_IMAGE_KEY = "base64_image"

    async def _acreate_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        summarize_tasks = [self._acreate_single_summary(info, config) for info in tqdm(information)]
        return await gather(*summarize_tasks)

    async def _acreate_single_summary(self, information: Document, config: Optional[RunnableConfig]) -> Document:
        summary = await self._summarizer.ainvoke(information.page_content, config)
        meta = {key: value for key, value in information.metadata.items() if key != self.BASE64_IMAGE_KEY}
        meta["id"] = sha256(str.encode(summary)).hexdigest()
        meta["related"].append(information.metadata["id"])
        meta["type"] = ContentType.SUMMARY.value
        return Document(metadata=meta, page_content=summary)
