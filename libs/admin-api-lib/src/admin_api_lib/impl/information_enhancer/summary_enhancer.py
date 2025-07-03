"""Module with SummaryEnhancer class that enhances information by generating summaries using a provided Summarizer."""

from abc import abstractmethod
from typing import Optional

from admin_api_lib.impl.settings.chunker_settings import ChunkerSettings
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig, ensure_config

from admin_api_lib.information_enhancer.information_enhancer import (
    InformationEnhancer,
    RetrieverInput,
    RetrieverOutput,
)
from admin_api_lib.summarizer.summarizer import Summarizer
from rag_core_lib.impl.data_types.content_type import ContentType


class SummaryEnhancer(InformationEnhancer):
    """The SummaryEnhancer enhances information by generating summaries using a provided Summarizer instance.

    Attributes
    ----------
    INFORMATION_METADATA_TYPE : str
        A constant string representing the type of information metadata.
    """

    INFORMATION_METADATA_TYPE = "type"

    def __init__(self, summarizer: Summarizer, chunker_settings: ChunkerSettings = None):
        """
        Initialize the SummaryEnhancer with a given Summarizer instance.

        Parameters
        ----------
        summarizer : Summarizer
            An instance of the Summarizer class used to generate summaries.
        """
        super().__init__()
        self._summarizer = summarizer
        self._chunker_settings = chunker_settings

    @staticmethod
    def _is_relevant(information: Document) -> bool:
        match information.metadata.get(SummaryEnhancer.INFORMATION_METADATA_TYPE, ContentType.SUMMARY):  # noqa:R503
            case ContentType.SUMMARY | ContentType.IMAGE:
                return False
            case _:
                return True

    async def ainvoke(self, information: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        """
        Asynchronously invokes the summary enhancer on the provided information.

        Parameters
        ----------
        information : RetrieverInput
            The input information to be processed and summarized.
        config : Optional[RunnableConfig], optional
            Configuration for the runnable, by default None.

        Returns
        -------
        RetrieverOutput
            The summarized output of the provided information.
        """
        config = ensure_config(config)
        pieces_to_summarize = [info for info in information if self._is_relevant(info)]
        return await self._acreate_summary(pieces_to_summarize, config)

    @abstractmethod
    async def _acreate_summary(
        self, information: list[Document], config: Optional[RunnableConfig]
    ) -> list[Document]: ...
