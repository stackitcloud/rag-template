import logging
import traceback
from typing import Optional

from langchain_core.runnables import (
    RunnableConfig,
    Runnable,
    ensure_config,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore

from admin_api_lib.summarizer.summarizer import SummarizerInput, SummarizerOutput, Summarizer

logger = logging.getLogger(__name__)


class LangchainSummarizer(Summarizer):
    def __init__(
        self,
        langfuse_manager: LangfuseManager,
        chunker: RecursiveCharacterTextSplitter,
        semaphore: AsyncThreadsafeSemaphore,
    ):
        self._chunker = chunker
        self._langfuse_manager = langfuse_manager
        self._semaphore = semaphore

    async def ainvoke(self, query: SummarizerInput, config: Optional[RunnableConfig] = None) -> SummarizerOutput:
        assert query, "Query is empty: %s" % query  # noqa S101
        config = ensure_config(config)
        tries_remaining = config.get("configurable", {}).get("tries_remaining", 3)
        logger.debug("Tries remaining %d" % tries_remaining)

        if tries_remaining < 0:
            raise Exception("Summary creation failed.")
        document = Document(page_content=query)
        langchain_documents = self._chunker.split_documents([document])

        outputs = []
        for langchain_document in langchain_documents:
            async with self._semaphore:
                try:
                    outputs.append(
                        await self._create_chain().ainvoke({"text": langchain_document.page_content}, config)
                    )
                except Exception as e:
                    logger.error("Error in summarizing langchain doc: %s %s", e, traceback.format_exc())
                    config["tries_remaining"] = tries_remaining - 1
                    outputs.append(
                        await self._create_chain().ainvoke({"text": langchain_document.page_content}, config)
                    )

        if len(outputs) == 1:
            return outputs[0]
        summary = " ".join(outputs)
        logger.debug(
            "Reduced number of chars from %d to %d"
            % (len("".join([x.page_content for x in langchain_documents])), len(summary))
        )
        return await self.ainvoke(summary, config)

    def _create_chain(self) -> Runnable:
        return self._langfuse_manager.get_base_prompt(self.__class__.__name__) | self._langfuse_manager.get_base_llm(
            self.__class__.__name__
        )
