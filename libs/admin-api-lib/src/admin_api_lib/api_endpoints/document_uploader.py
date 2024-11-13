from abc import ABC, abstractmethod

from fastapi import Request, UploadFile


class DocumentUploader(ABC):
    """Abstract base class for document upload endpoint."""

    @abstractmethod
    async def aupload_documents_post(self, body: UploadFile, request: Request) -> None:
        """Upload PDF documents."""
        pass
