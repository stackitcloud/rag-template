"""Module for the implementation of the RagApi class."""

import logging
from asyncio import run
from threading import Thread

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.api_endpoints.information_piece_remover import InformationPieceRemover
from rag_core_api.api_endpoints.information_piece_uploader import (
    InformationPiecesUploader,
)
from rag_core_api.apis.rag_api_base import BaseRagApi
from rag_core_api.dependency_container import DependencyContainer
from rag_core_api.evaluator.evaluator import Evaluator
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.information_piece import InformationPiece

logger = logging.getLogger(__name__)


class RagApi(BaseRagApi):
    """
    RagApi class for handling various endpoints of the RAG API.

    This class provides asynchronous methods to handle chat requests, evaluate the RAG,
    remove information pieces, and upload information pieces. It manages background threads
    for evaluation tasks and uses dependency injection for its dependencies.
    """

    def __init__(self):
        """Initialize the instance of the class."""
        super().__init__()
        self._background_threads = []

    @inject
    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
        chat_endpoint: Chat = Depends(Provide[DependencyContainer.chat_endpoint]),
    ) -> ChatResponse:
        """
        Asynchronously handles the chat endpoint for the RAG API.

        Parameters
        ----------
        session_id : str
            The session ID for the chat.
        chat_request : ChatRequest
            The chat request payload.
        chat_endpoint : Chat, optional
            The chat endpoint dependency.

        Returns
        -------
        ChatResponse
            The chat response if the chat task completes successfully.
        """
        return await chat_endpoint.achat(session_id, chat_request)

    @inject
    async def evaluate(
        self,
        evaluator: Evaluator = Depends(Provide[DependencyContainer.evaluator]),
    ) -> None:
        """
        Asynchronously evaluates the RAG with the given evaluator and manages background threads.

        This method cleans up any non-alive threads from the background thread list,
        starts a new thread to run the evaluator's asynchronous evaluation method,
        and appends the new thread to the background thread list.

        Parameters
        ----------
        evaluator : Evaluator, optional
            The evaluator instance to be used for evaluation. It is provided by dependency injection.

        Returns
        -------
        None
        """
        # cleanup threads
        self._background_threads = [t for t in self._background_threads if t.is_alive()]
        thread = Thread(target=lambda: run(evaluator.aevaluate()))
        thread.start()
        self._background_threads.append(thread)

    @inject
    async def remove_information_piece(
        self,
        delete_request: DeleteRequest,
        information_pieces_remover: InformationPieceRemover = Depends(
            Provide[DependencyContainer.information_pieces_remover]
        ),
    ) -> None:
        """
        Asynchronously Removes information pieces based on the provided delete request.

        Parameters
        ----------
        delete_request : DeleteRequest
            The request containing the details of the information pieces to be deleted.
        information_pieces_remover : InformationPieceRemover, optional
            The remover service used to delete the information pieces
            (default Depends(Provide[DependencyContainer.information_pieces_remover])).

        Returns
        -------
        None
        """
        information_pieces_remover.remove_information_piece(delete_request)

    @inject
    async def upload_information_piece(
        self,
        information_piece: list[InformationPiece],
        information_pieces_uploader: InformationPiecesUploader = Depends(
            Provide[DependencyContainer.information_pieces_uploader]
        ),
    ) -> None:
        """
        Asynchronously uploads a list of information pieces.

        Parameters
        ----------
        information_piece : list[InformationPiece]
            A list of InformationPiece objects to be uploaded.
        information_pieces_uploader : InformationPiecesUploader, optional
            An instance of InformationPiecesUploader
            (default Depends(Provide[DependencyContainer.information_pieces_uploader]))

        Returns
        -------
        None
        """
        information_pieces_uploader.upload_information_piece(information_piece)
