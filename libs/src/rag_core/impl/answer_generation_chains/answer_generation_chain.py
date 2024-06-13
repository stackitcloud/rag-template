from abc import ABC
from typing import Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


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
        self._chain = (
            RunnablePassthrough.assign(context=(lambda x: self.format_docs(x["retrieved_documents"])))
            | prompt
            | llm
            | StrOutputParser()
        )

    def invoke(self, input: RunnableInput, config: Optional[RunnableConfig] = None, **kwargs: Any) -> RunnableOutput:
        prompt_input = input.model_dump()
        return self._chain.invoke(prompt_input, config=config)

    @staticmethod
    def format_docs(docs: List[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)
