"""Module containing the implementation of the Admin API."""

import logging

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request, Response, UploadFile

from admin_api_lib.api_endpoints.confluence_loader import ConfluenceLoader
from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.api_endpoints.document_reference_retriever import (
    DocumentReferenceRetriever,
)
from admin_api_lib.api_endpoints.document_uploader import DocumentUploader
from admin_api_lib.api_endpoints.documents_status_retriever import (
    DocumentsStatusRetriever,
)
from admin_api_lib.apis.admin_api_base import BaseAdminApi
from admin_api_lib.dependency_container import DependencyContainer
from admin_api_lib.models.document_status import DocumentStatus

logger = logging.getLogger(__name__)


class AdminApi(BaseAdminApi):
    """The Class for the Admin API.

    AdminApi class provides various asynchronous methods to interact with documents, including deleting,
    retrieving status, loading from Confluence, retrieving by reference ID, and uploading documents.
    """

    def __init__(self):
        """
        Initialize the AdminAPI class.

        This constructor calls the parent class's initializer and sets up
        an empty list to hold background threads.
        """
        super().__init__()
        self._background_threads = []

    @inject
    async def delete_document(
        self,
        identification: str,
        document_deleter: DocumentDeleter = Depends(Provide[DependencyContainer.document_deleter]),
    ) -> None:
        """
        Delete a document asynchronously.

        Parameters
        ----------
        identification : str
            The unique identifier of the document to be deleted.
        document_deleter : DocumentDeleter
            The document deleter instance, injected by dependency injection
            (default is Depends(Provide[DependencyContainer.document_deleter])).

        Returns
        -------
        None
        """
        await document_deleter.adelete_document(identification)

    @inject
    async def get_all_documents_status(
        self,
        document_status_retriever: DocumentsStatusRetriever = Depends(
            Provide[DependencyContainer.documents_status_retriever]
        ),
    ) -> list[DocumentStatus]:
        """
        Asynchronously retrieve the status of all documents.

        Parameters
        ----------
        document_status_retriever : DocumentsStatusRetriever
            An instance of DocumentsStatusRetriever
            (default is Depends(Provide[DependencyContainer.documents_status_retriever])).

        Returns
        -------
        list[DocumentStatus]
            A list containing the status of all documents.
        """
        return await document_status_retriever.aget_all_documents_status()

    @inject
    async def load_confluence_post(
        self,
        confluence_loader: ConfluenceLoader = Depends(Provide[DependencyContainer.confluence_loader]),
    ) -> None:
        """
        Asynchronously loads a Confluence space using the provided ConfluenceLoader.

        Parameters
        ----------
        confluence_loader : ConfluenceLoader
            The ConfluenceLoader instance to use for loading the post. This is injected by dependency injection
            (default is Depends(Provide[DependencyContainer.confluence_loader])).

        Returns
        -------
        None
        """
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
        Retrieve the document with the given identification.

        Parameters
        ----------
        identification : str
            The identification of the document.
        document_reference_retriever : DocumentReferenceRetriever, optional
            The service to retrieve the document reference.
            Defaults to Depends(Provide[DependencyContainer.document_reference_retriever]).

        Returns
        -------
        Response
            The document in binary form.
        """
        return await document_reference_retriever.adocument_reference_id_get(identification)

    @inject
    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
        document_uploader: DocumentUploader = Depends(Provide[DependencyContainer.document_uploader]),
    ) -> None:
        """
        Handle the POST request to upload documents.

        Parameters
        ----------
        body : UploadFile
            The file to be uploaded.
        request : Request
            The request object containing metadata about the request.
        document_uploader : DocumentUploader, optional
            The document uploader dependency, by default provided by DependencyContainer.

        Returns
        -------
        None
        """
        await document_uploader.aupload_documents_post(body, request)
