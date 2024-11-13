# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.information_piece import InformationPiece


class BaseRagApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseRagApi.subclasses = BaseRagApi.subclasses + (cls,)

    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse:
        ...

    async def evaluate(
        self,
    ) -> None:
        ...

    async def remove_information_piece(
        self,
        delete_request: DeleteRequest,
    ) -> None:
        ...

    async def upload_information_piece(
        self,
        information_piece: List[InformationPiece],
    ) -> None:
        ...
