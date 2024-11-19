import logging

from admin_api_lib.api_endpoints.confluence_loader import ConfluenceLoader
from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.api_endpoints.document_reference_retriever import DocumentReferenceRetriever
from admin_api_lib.api_endpoints.document_uploader import DocumentUploader
from admin_api_lib.api_endpoints.documents_status_retriever import DocumentsStatusRetriever
from admin_api_lib.apis.admin_api_base import BaseAdminApi
from admin_api_lib.dependency_container import DependencyContainer
from admin_api_lib.models.document_status import DocumentStatus
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request, Response, UploadFile

logger = logging.getLogger(__name__)


class AdminApi(BaseAdminApi):
    DOCUMENT_METADATA_TYPE_KEY = "type"

    def __init__(self):
        super().__init__()
        self._background_threads = []

    @inject
    async def delete_document(
        self,
        identification: str,
        document_deleter: DocumentDeleter = Depends(Provide[DependencyContainer.document_deleter]),
    ) -> None:
        await document_deleter.adelete_document(identification)

    @inject
    async def get_all_documents_status(
        self,
        document_status_retriever: DocumentsStatusRetriever = Depends(
            Provide[DependencyContainer.documents_status_retriever]
        ),
    ) -> list[DocumentStatus]:
        return await document_status_retriever.aget_all_documents_status()

    @inject
    async def load_confluence_post(
        self,
        confluence_loader: ConfluenceLoader = Depends(Provide[DependencyContainer.confluence_loader]),
    ) -> None:
        await confluence_loader.aload_from_confluence()

    @inject
    async def document_reference_id_get(
        self,
        identification: str,
        document_reference_retriever: DocumentReferenceRetriever = Depends(
            Provide[DependencyContainer.document_reference_retriever]
        ),
    ) -> Response:
        """
        Retrieves the document with the given identification.

        Args:
            identification (str): The identification of the document.
            document_reference_retriever (DocumentReferenceRetriever, optional):
                The service to retrieve the document reference.
                Defaults to Depends(Provide[DependencyContainer.document_reference_retriever]).

        Returns:
            Response: The document in binary form.
        """

        return await document_reference_retriever.adocument_reference_id_get(identification)

    @inject
    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
        document_uploader: DocumentUploader = Depends(Provide[DependencyContainer.document_uploader]),
    ) -> None:
        await document_uploader.aupload_documents_post(body, request)
