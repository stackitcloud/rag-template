import json
import logging

from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.file_services.file_service import FileService
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.rag_backend_client.openapi_client.models.delete_request import DeleteRequest
from admin_api_lib.rag_backend_client.openapi_client.models.key_value_pair import KeyValuePair
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class DefaultDocumentDeleter(DocumentDeleter):
    def __init__(self, file_service: FileService, rag_api: RagApi, key_value_store: FileStatusKeyValueStore):
        self._file_service = file_service
        self._rag_api = rag_api
        self._key_value_store = key_value_store

    async def adelete_document(self, identification: str) -> None:
        error_messages = ""
        # Delete the document from file service and vector database
        logger.debug("Deleting existing document: %s", identification)
        try:
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
