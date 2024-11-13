from abc import ABC
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough

from rag_core_lib.chains.async_chain import AsyncChain
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_api.impl.graph.graph_state.graph_state import AnswerGraphState

RunnableInput = AnswerGraphState
RunnableOutput = str


class AnswerGenerationChain(AsyncChain[RunnableInput, RunnableOutput], ABC):
    """
    Base class for LLM answer generation chain.
    """

    def __init__(self, langfuse_manager: LangfuseManager):
        self._langfuse_manager = langfuse_manager

    @staticmethod
    def _format_docs(docs: list[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    async def ainvoke(
        self, chain_input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> RunnableOutput:
        return await self._create_chain().ainvoke(chain_input, config=config)

    def _create_chain(self) -> Runnable:
        return (
            RunnablePassthrough.assign(context=(lambda x: self._format_docs(x["langchain_documents"])))
            | self._langfuse_manager.get_base_prompt(self.__class__.__name__)
            | self._langfuse_manager.get_base_llm(self.__class__.__name__)
        )
