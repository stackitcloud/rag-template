# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse
from rag_core.models.delete_request import DeleteRequest
from rag_core.models.search_request import SearchRequest
from rag_core.models.search_response import SearchResponse
from rag_core.models.upload_source_document import UploadSourceDocument


class BaseRagApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseRagApi.subclasses = BaseRagApi.subclasses + (cls,)

    def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
    ) -> ChatResponse: ...

    def remove_source_documents(
        self,
        delete_request: DeleteRequest,
    ) -> None: ...

    def search(
        self,
        search_request: SearchRequest,
    ) -> SearchResponse: ...

    def upload_source_documents(
        self,
        upload_source_document: List[UploadSourceDocument],
    ) -> None: ...
