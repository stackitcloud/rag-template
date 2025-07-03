"""Module containing the base RAG API class."""

# coding: utf-8
# flake8: noqa: D105

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.information_piece import InformationPiece


class BaseRagApi:
    """Base class for RAG API.

    This class serves as the base for the RAG API implementations. It provides
    asynchronous methods for handling chat, evaluating the RAG, removing information
    pieces, and uploading information pieces to a vector database.

    Attributes
    subclasses : ClassVar[Tuple]
        A tuple that holds all subclasses of BaseRagApi.
    """

    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseRagApi.subclasses = BaseRagApi.subclasses + (cls,)

    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        """
        Asynchronously handles the chat endpoint for the RAG API.

        Parameters
        ----------
        request : Request
            The request object.
        session_id : str
            The session ID for the chat.
        chat_request : ChatRequest, optional
            The chat request payload

        Returns
        -------
        ChatResponse or None
            The chat response if the chat task completes successfully, otherwise None.
        """

    async def evaluate(
        self,
    ) -> None:
        """
        Asynchronously evaluate the RAG.

        Returns
        -------
        None
        """

    async def remove_information_piece(
        self,
        delete_request: DeleteRequest,
    ) -> None:
        """
        Asynchronously removes information pieces.

        This endpoint removes information pieces based on the provided delete request.

        Parameters
        ----------
        delete_request : DeleteRequest
            The request body containing the details for the information piece to be removed.

        Returns
        -------
        None
        """

    async def upload_information_piece(
        self,
        information_piece: List[InformationPiece],
    ) -> None:
        """
        Asynchronously uploads information pieces for vectordatabase.

        This endpoint allows for the upload of information pieces to the vector database.

        Parameters
        ----------
        information_piece : List[InformationPiece]
            A list of information pieces to be uploaded (default None).

        Returns
        -------
        None
        """
