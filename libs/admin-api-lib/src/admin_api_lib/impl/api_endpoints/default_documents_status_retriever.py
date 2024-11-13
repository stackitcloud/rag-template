import logging

from admin_api_lib.api_endpoints.documents_status_retriever import DocumentsStatusRetriever
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.models.document_status import DocumentStatus

logger = logging.getLogger(__name__)


class DefaultDocumentsStatusRetriever(DocumentsStatusRetriever):
    def __init__(self, key_value_store: FileStatusKeyValueStore):
        self._key_value_store = key_value_store

    async def aget_all_documents_status(self) -> list[DocumentStatus]:
        all_documents = self._key_value_store.get_all()
        return [DocumentStatus(name=x[0], status=x[1]) for x in all_documents]
