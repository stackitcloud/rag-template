"""Module for the DocumentUploader abstract base class."""

from abc import ABC, abstractmethod

from fastapi import Request, UploadFile


class DocumentUploader(ABC):
    """Abstract base class for document upload endpoint."""

    @abstractmethod
    async def aupload_documents_post(self, body: UploadFile, request: Request) -> None:
        """
        Upload documents asynchronously, currently supported formats are: PDF, DOCX, XML, PPTX.

        Parameters
        ----------
        body : UploadFile
            The uploaded file.
        request : Request
            The request object.

        Returns
        -------
        None
        """
