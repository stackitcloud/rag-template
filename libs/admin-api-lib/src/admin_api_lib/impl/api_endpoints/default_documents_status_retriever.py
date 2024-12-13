"""Module for the DefaultDocumentsStatusRetriever class."""

import logging

from admin_api_lib.api_endpoints.documents_status_retriever import (
    DocumentsStatusRetriever,
)
from admin_api_lib.impl.key_db.file_status_key_value_store import (
    FileStatusKeyValueStore,
)
from admin_api_lib.models.document_status import DocumentStatus

logger = logging.getLogger(__name__)


class DefaultDocumentsStatusRetriever(DocumentsStatusRetriever):
    """The DefaultDocumentsStatusRetriever retrieves the status of all documents from a key-value store."""

    def __init__(self, key_value_store: FileStatusKeyValueStore):
        """
        Initialize the DefaultDocumentsStatusRetriever.

        Parameters
        ----------
        key_value_store : FileStatusKeyValueStore
            The key-value store for storing filename and the corresponding status.
        """
        self._key_value_store = key_value_store

    async def aget_all_documents_status(self) -> list[DocumentStatus]:
        """
        Asynchronously retrieves the status of all documents.

        Returns
        -------
        list[DocumentStatus]
            A list containing the status of all documents, where each document's
            status is represented by a DocumentStatus object.
        """
        all_documents = self._key_value_store.get_all()
        return [DocumentStatus(name=x[0], status=x[1]) for x in all_documents]
