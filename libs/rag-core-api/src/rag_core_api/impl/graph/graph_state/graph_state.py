"""Module for the AnswerGraphState class."""

import operator
from typing import Annotated

from langchain_core.documents import Document
from typing_extensions import TypedDict

from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.information_piece import InformationPiece


class AnswerGraphState(TypedDict):
    """Represent the state of the answer graph.

    Attributes
    ----------
    question : str
        The original question asked.
    language : str
        The language the question has been asked in.
    rephrased_question : str
        The rephrased version of the original question.
    history : str
        The history of interactions or context leading up to the current state.
    information_pieces : list[InformationPiece]
        A list of information pieces relevant to the question.
    langchain_documents : list[Document]
        A list of documents processed by LangChain.
    answer_text : str | None
        The text of the answer, if available (default None).
    response : ChatResponse | None
        The chat response object, if available (default None).
    additional_info : dict | None
        Any additional information (default None).
    error_messages : list[str]
        A list of error messages encountered.
    finish_reasons : list[str]
        A list of reasons why the process finished.
    """

    question: str
    language: str
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
        language="en",
    ) -> "AnswerGraphState":
        """
        Create an instance of AnswerGraphState.

        Parameters
        ----------
        cls : type
            The class type.
        question : str
            The question being asked.
        history : list
            The history of previous interactions.
        error_messages : list
            List of error messages encountered.
        finish_reasons : list
            List of reasons for finishing the process.
        information_pieces : list
            Pieces of information relevant to the question.
        langchain_documents : list
            Documents used by the LangChain model.
        rephrased_question : str
            The rephrased version of the question (default None).
        answer_text : str
            The text of the answer (default None).
        response : dict
            The response data (default None).
        additional_info : dict
            Any additional information (default None).
        language : str
            The language the question has been asked in (default en).

        Returns
        -------
        AnswerGraphState
            An instance of AnswerGraphState.
        """
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
            language=language,
        )
