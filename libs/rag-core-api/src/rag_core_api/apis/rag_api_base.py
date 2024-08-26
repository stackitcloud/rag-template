# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import BackgroundTasks
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.search_request import SearchRequest
from rag_core_api.models.search_response import SearchResponse
from rag_core_api.models.upload_source_document import UploadSourceDocument


class BaseRagApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseRagApi.subclasses = BaseRagApi.subclasses + (cls,)

    async def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse: ...

    async def evaluate(
        self,
        background_tasks: BackgroundTasks,
    ) -> None: ...

    async def remove_source_documents(
        self,
        delete_request: DeleteRequest,
    ) -> None: ...

    async def search(
        self,
        search_request: SearchRequest,
    ) -> SearchResponse: ...

    async def upload_source_documents(
        self,
        upload_source_document: List[UploadSourceDocument],
    ) -> None: ...
