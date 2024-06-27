import logging

from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from langchain_core.runnables import RunnableConfig

from rag_core.api_endpoints.chat_chain import ChatChain
from rag_core.api_endpoints.searcher import Searcher
from rag_core.api_endpoints.source_documents_remover import SourceDocumentsRemover
from rag_core.api_endpoints.source_documents_uploader import SourceDocumentsUploader
from rag_core.dependency_container import DependencyContainer
from rag_core.models.chat_request import ChatRequest
from rag_core.models.chat_response import ChatResponse
from rag_core.models.delete_request import DeleteRequest
from rag_core.models.search_request import SearchRequest
from rag_core.models.search_response import SearchResponse
from rag_core.models.upload_source_document import UploadSourceDocument
from rag_core.apis.rag_api_base import BaseRagApi
from rag_core.apis.rag_api_base import BaseRagApi
from rag_core.models.search_response import SearchResponse


logger = logging.getLogger(__name__)


class RagApi(BaseRagApi):

    @inject
    def chat(
        self,
        session_id: str,
        chat_request: ChatRequest,
        chat_chain: ChatChain = Depends(Provide[DependencyContainer.traced_chat_chain]),
    ) -> ChatResponse:
        config = RunnableConfig(tags=[], callbacks=None, recursion_limit=25, metadata={"session_id": session_id})
        return chat_chain.invoke(chat_request, config)

    @inject
    def remove_source_documents(
        self,
        delete_request: DeleteRequest,
        source_documents_remover: SourceDocumentsRemover = Depends(
            Provide[DependencyContainer.source_documents_remover]
        ),
    ) -> None:
        source_documents_remover.remove_source_documents(delete_request)

    @inject
    def search(
        self,
        search_request: SearchRequest,
        searcher: Searcher = Depends(Provide[DependencyContainer.searcher]),
    ) -> SearchResponse:
        return searcher.search(search_request)

    @inject
    def upload_source_documents(
        self,
        upload_source_document: list[UploadSourceDocument],
        source_documents_uploader: SourceDocumentsUploader = Depends(
            Provide[DependencyContainer.source_documents_uploader]
        ),
    ) -> None:
        source_documents_uploader.upload_source_documents(upload_source_document)
