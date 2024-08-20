import logging
from typing import Optional
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableConfig,
    ensure_config,
)

from admin_backend.impl.prompt_templates.summarize_prompt import SUMMARIZE_PROMPT
from admin_backend.summarizer.summarizer import RetrieverInput, RetrieverOutput, Summarizer

logger = logging.getLogger(__name__)


class LangchainSummarizer(Summarizer):
    def __init__(
        self,
        llm,
    ) -> None:
        super().__init__()
        self._llm = llm
        self._prompt = SUMMARIZE_PROMPT
        self._chain = LLMChain(
            llm=self._llm,
            prompt=self._prompt,
            output_parser=StrOutputParser(),
        )

    def invoke(self, query: RetrieverInput, config: Optional[RunnableConfig] = None) -> RetrieverOutput:
        config = ensure_config(config)
        tries_remaining = config.get("tries_remaining", 3)

        if tries_remaining < 0:
            raise Exception("Summary creation failed.")
        try:
            return self._chain.invoke({"text": query}, config)["text"]
        except Exception as e:
            logger.error(e)
            config["tries_remaining"] = tries_remaining - 1
            return self.invoke(query, config)
