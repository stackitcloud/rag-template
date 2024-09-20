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
    source_documents: list[SourceDocument] | None
    langchain_documents: list[Document] | None
    answer_text: str | None
    response: ChatResponse | None
    retries: int
    is_harmful: bool
    is_from_context: bool
    answer_is_relevant: bool
    additional_info: dict | None
    error_message: str | None
    finish_reason: str | None

    @classmethod
    def create(
        cls,
        question,
        history,
        rephrased_question=None,
        source_documents=None,
        answer_text=None,
        response=None,
        retries=0,
        is_harmful=True,
        is_from_context=False,
        answer_is_relevant=False,
        additional_info=None,
        error_message=None,
        finish_reason=None,
    ) -> "AnswerGraphState":
        return AnswerGraphState(
            question=question,
            history=history,
            rephrased_question=rephrased_question,
            source_documents=source_documents,
            answer_text=answer_text,
            response=response,
            retries=retries,
            is_harmful=is_harmful,
            is_from_context=is_from_context,
            answer_is_relevant=answer_is_relevant,
            additional_info=additional_info,
            error_message=error_message,
            finish_reason=finish_reason,
        )
