import operator
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.documents import Document

from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.information_piece import InformationPiece


class AnswerGraphState(TypedDict):
    """
    Represents the state of the answer graph.

    """

    question: str
    rephrased_question: str
    history: str
    information_pieces: Annotated[list[InformationPiece], operator.add]
    langchain_documents: Annotated[list[Document], operator.add]
    answer_text: str | None
    response: ChatResponse | None
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
        information_pieces,
        langchain_documents,
        rephrased_question=None,
        answer_text=None,
        response=None,
        additional_info=None,
    ) -> "AnswerGraphState":
        return AnswerGraphState(
            question=question,
            history=history,
            rephrased_question=rephrased_question,
            information_pieces=information_pieces,
            langchain_documents=langchain_documents,
            answer_text=answer_text,
            response=response,
            additional_info=additional_info,
            error_messages=error_messages,
            finish_reasons=finish_reasons,
        )
