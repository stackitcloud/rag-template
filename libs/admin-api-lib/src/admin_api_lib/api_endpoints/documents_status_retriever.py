"""Module abstract base class for the DocumentsStatusRetriever."""

from abc import ABC, abstractmethod

from admin_api_lib.models.document_status import DocumentStatus


class DocumentsStatusRetriever(ABC):
    """Abstract base class for retrieving all documents."""

    @abstractmethod
    async def aget_all_documents_status(self) -> list[DocumentStatus]:
        """
        Get all documents and their statuses asynchronously.

        Returns
        -------
        list[DocumentStatus]
            A list containing document names and their statuses.
        """
