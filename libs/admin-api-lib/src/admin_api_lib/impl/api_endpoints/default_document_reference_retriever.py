"""Module for the DefaultDocumentReferenceRetriever class."""

import io
import logging
import traceback

from fastapi import HTTPException, Response, status

from admin_api_lib.api_endpoints.document_reference_retriever import (
    DocumentReferenceRetriever,
)
from admin_api_lib.file_services.file_service import FileService

logger = logging.getLogger(__name__)


class DefaultDocumentReferenceRetriever(DocumentReferenceRetriever):
    """A class to retrieve document references using a file service."""

    def __init__(self, file_service: FileService):
        """
        Initialize the DefaultDocumentReferenceRetriever.

        Parameters
        ----------
        file_service : FileService
            An instance of FileService used to handle file operations.
        """
        self._file_service = file_service

    async def adocument_reference_id_get(self, identification: str) -> Response:
        """
        Retrieve the document with the given identification asynchronously.

        Parameters
        ----------
        identification : str
            The identification string of the document.

        Returns
        -------
        Response
            The document in binary form wrapped in a FastAPI Response object.

        Raises
        ------
        HTTPException
            If the document with the given identification is not found or any other value error occurs.
        """
        try:
            logger.debug("START retrieving document with id: %s", identification)
            document_buffer = io.BytesIO()
            try:
                self._file_service.download_file(identification, document_buffer)
                logger.debug("DONE retrieving document with id: %s", identification)
                document_data = document_buffer.getvalue()
            except Exception as e:
                logger.error(
                    "Error retrieving document with id: %s. Error: %s %s", identification, e, traceback.format_exc()
                )
                raise ValueError(f"Document with id '{identification}' not found.")
            finally:
                document_buffer.close()
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        media_type = "application/pdf" if identification.endswith(".pdf") else "application/octet-stream"
        headers = {
            "Content-Disposition": f'inline; filename="{identification.encode("utf-8").decode()}"',
            "Content-Type": media_type,
        }
        return Response(document_data, status_code=200, headers=headers, media_type=media_type)
