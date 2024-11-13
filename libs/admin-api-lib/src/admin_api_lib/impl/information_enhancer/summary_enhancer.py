from abc import abstractmethod
from typing import Optional

from langchain_core.documents import Document
from langchain_core.runnables import (
    RunnableConfig,
    ensure_config,
)
from rag_core_lib.impl.data_types.content_type import ContentType

from admin_api_lib.information_enhancer.information_enhancer import (
    InformationEnhancer,
    RetrieverInput,
    RetrieverOutput,
)
from admin_api_lib.summarizer.summarizer import Summarizer


class SummaryEnhancer(InformationEnhancer):
    INFORMATION_METADATA_TYPE = "type"

    def __init__(self, summarizer: Summarizer):
        super().__init__()
        self._summarizer = summarizer

    @staticmethod
    def _is_relevant(information: Document) -> bool:
        match information.metadata.get(SummaryEnhancer.INFORMATION_METADATA_TYPE, ContentType.SUMMARY):  # noqa:R503
            case ContentType.SUMMARY | ContentType.IMAGE:
                return False
            case _:
                return True

    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        config = ensure_config(config)
        pieces_to_summarize = [info for info in information if self._is_relevant(info)]
        return await self._acreate_summary(pieces_to_summarize, config)

    @abstractmethod
    async def _acreate_summary(self, information: list[Document], config: Optional[RunnableConfig]) -> list[Document]:
        ...
