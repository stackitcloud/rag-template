import io
import logging
import traceback

from admin_api_lib.api_endpoints.document_reference_retriever import DocumentReferenceRetriever
from admin_api_lib.file_services.file_service import FileService
from fastapi import HTTPException, Response, status

logger = logging.getLogger(__name__)


class DefaultDocumentReferenceRetriever(DocumentReferenceRetriever):
    def __init__(self, file_service: FileService):
        self._file_service = file_service

    async def adocument_reference_id_get(self, identification: str) -> Response:
        """
        Retrieves the document with the given name.

        Args:
            document_name (str): The name of the document.
            file_service (FileService): The file service.

        Returns:
            bytes: The document in binary form.
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
