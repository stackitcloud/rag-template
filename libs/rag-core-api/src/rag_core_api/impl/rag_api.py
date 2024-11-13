from asyncio import run
import logging
from threading import Thread

from fastapi import Depends
from dependency_injector.wiring import Provide, inject

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.information_piece import InformationPiece
from rag_core_api.api_endpoints.information_piece_remover import InformationPieceRemover
from rag_core_api.api_endpoints.information_piece_uploader import InformationPiecesUploader
from rag_core_api.dependency_container import DependencyContainer
from rag_core_api.apis.rag_api_base import BaseRagApi
from rag_core_api.evaluator.evaluator import Evaluator


logger = logging.getLogger(__name__)


class RagApi(BaseRagApi):
    def __init__(self):
        super().__init__()
        self._background_threads = []

    @inject
    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
        chat_endpoint: Chat = Depends(Provide[DependencyContainer.chat_endpoint]),
    ) -> ChatResponse:
        return await chat_endpoint.achat(session_id, chat_request)

    @inject
    async def evaluate(
        self,
        evaluator: Evaluator = Depends(Provide[DependencyContainer.evaluator]),
    ) -> None:
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
        information_pieces_remover.remove_information_piece(delete_request)

    @inject
    async def upload_information_piece(
        self,
        information_piece: list[InformationPiece],
        information_pieces_uploader: InformationPiecesUploader = Depends(
            Provide[DependencyContainer.information_pieces_uploader]
        ),
    ) -> None:
        information_pieces_uploader.upload_information_piece(information_piece)
