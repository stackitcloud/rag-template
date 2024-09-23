import operator
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.documents import Document

from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.source_document import SourceDocument


class AnswerGraphState(TypedDict):
    """
    Represents the state of the answer graph.

    """

    question: str
    rephrased_question: str
    history: str
    source_documents: Annotated[list[SourceDocument], operator.add]
    langchain_documents: Annotated[list[Document], operator.add]
    answer_text: str | None
    response: ChatResponse | None
    retries: int
    is_harmful: bool
    is_from_context: bool
    answer_is_relevant: bool
    additional_info: dict | None
    error_messages: Annotated[list[str], operator.add]
    finish_reasons: Annotated[list[str], operator.add]

    @classmethod
    def create(
        cls,
        question,
        history,
        error_messages,
        finish_reasons,
        source_documents,
        langchain_documents,
        rephrased_question=None,
        answer_text=None,
        response=None,
        retries=0,
        is_harmful=True,
        is_from_context=False,
        answer_is_relevant=False,
        additional_info=None,
    ) -> "AnswerGraphState":
        return AnswerGraphState(
            question=question,
            history=history,
            rephrased_question=rephrased_question,
            source_documents=source_documents,
            langchain_documents=langchain_documents,
            answer_text=answer_text,
            response=response,
            retries=retries,
            is_harmful=is_harmful,
            is_from_context=is_from_context,
            answer_is_relevant=answer_is_relevant,
            additional_info=additional_info,
            error_messages=error_messages,
            finish_reasons=finish_reasons,
        )
