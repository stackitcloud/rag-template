from abc import ABC
from typing import Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough


from rag_core.impl.answer_generation_chains.answer_chain_input_data import (
    AnswerChainInputData,
)

RunnableInput = AnswerChainInputData
RunnableOutput = str


class AnswerGenerationChain(Runnable[RunnableInput, RunnableOutput], ABC):
    """
    Base class for LLM answer generation chain.
    """

    def __init__(self, llm: LLM, prompt: PromptTemplate):
        self._llm = llm
        self._chain = self._create_chain(prompt)

    def _create_chain(self, prompt: PromptTemplate) -> Runnable:
        return (
            RunnablePassthrough.assign(context=(lambda x: self._format_docs(x["retrieved_documents"])))
            | prompt
            | self._llm
        )

    def invoke(self, input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any) -> RunnableOutput:
        prompt_input = input.model_dump()
        return self._chain.invoke(prompt_input, config=config)

    @staticmethod
    def _format_docs(docs: List[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)
