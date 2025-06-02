"""Module for the DefaultDocumentDeleter class."""

import json
import logging

from fastapi import HTTPException

from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.file_services.file_service import FileService
from admin_api_lib.impl.key_db.file_status_key_value_store import (
    FileStatusKeyValueStore,
)
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.rag_backend_client.openapi_client.models.delete_request import (
    DeleteRequest,
)
from admin_api_lib.rag_backend_client.openapi_client.models.key_value_pair import (
    KeyValuePair,
)

logger = logging.getLogger(__name__)


class DefaultDocumentDeleter(DocumentDeleter):
    """A class used to delete documents from file storage and vector database."""

    def __init__(self, file_service: FileService, rag_api: RagApi, key_value_store: FileStatusKeyValueStore):
        """
        Initialize the DefaultDocumentDeleter.

        Parameters
        ----------
        file_service : FileService
            The service responsible for file operations with s3 storage.
        rag_api : RagApi
            The API client for interacting with the RAG backend system.
        key_value_store : FileStatusKeyValueStore
            The key-value store to store file names and the corresponding file statuses.
        """
        self._file_service = file_service
        self._rag_api = rag_api
        self._key_value_store = key_value_store

    async def adelete_document(self, identification: str, remove_from_key_value_store: bool = True) -> None:
        """
        Asynchronously delete a document identified by the given identification string.

        This method attempts to delete the document from both the S3 storage and the vector database.
        If any errors occur during the deletion process, an HTTPException is raised with the error messages.
        If the source document is from a service like Confluence, no document on the S3 storage exists, and nothing
        can be deleted from the S3 storage. However, this does not prevent the deletion of the document from the
        vector database. If the document does not exist on the S3 storage, the deletion process will continue.

        Parameters
        ----------
        identification : str
            The unique identifier of the document to be deleted.
        remove_from_key_value_store : bool, optional
            If True, the document will also be removed from the key-value store (default is True).

        Raises
        ------
        HTTPException
            If any errors occur during the deletion process, an HTTPException is raised with a 404 status code
            and the error messages.
        """
        error_messages = ""
        # Delete the document from file service and vector database
        logger.debug("Deleting existing document: %s", identification)
        try:
            if remove_from_key_value_store:
                self._key_value_store.remove(identification)
            self._file_service.delete_file(identification)
        except Exception as e:
            error_messages += f"Error while deleting {identification} from file storage\n {str(e)}\n"
        try:
            self._rag_api.remove_information_piece(
                DeleteRequest(metadata=[KeyValuePair(key="document", value=json.dumps(identification))])
            )
            logger.info("Deleted information pieces belonging to %s from rag.", identification)
        except Exception as e:
            error_messages += f"Error while deleting {identification} from vector db\n{str(e)}"
        if error_messages:
            raise HTTPException(404, error_messages)
