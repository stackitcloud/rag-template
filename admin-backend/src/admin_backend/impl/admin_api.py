from asyncio import run
import io
import logging
import tempfile
from pathlib import Path
import json
from threading import Thread
import traceback
import urllib

from admin_backend.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_backend.models.document_status import DocumentStatus
from admin_backend.models.status import Status
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Request, Response, UploadFile, status

from admin_backend.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_backend.apis.admin_api_base import BaseAdminApi
from admin_backend.dependency_container import DependencyContainer
from admin_backend.document_extractor_client.openapi_client.api.extractor_api import (
    ExtractorApi,
)
from admin_backend.document_extractor_client.openapi_client.models.extraction_request import (
    ExtractionRequest,
)
from admin_backend.file_services.file_service import FileService
from admin_backend.impl.chunker.chunker import Chunker
from admin_backend.information_enhancer.information_enhancer import (
    InformationEnhancer,
)
from admin_backend.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_backend.rag_backend_client.openapi_client.models.delete_request import DeleteRequest
from admin_backend.rag_backend_client.openapi_client.models.key_value_pair import KeyValuePair
from admin_backend.rag_backend_client.openapi_client.models.upload_source_document import UploadSourceDocument
from admin_backend.rag_backend_client.openapi_client.models.content_type import ContentType

logger = logging.getLogger(__name__)


class AdminApi(BaseAdminApi):
    DOCUMENT_METADATA_TYPE_KEY = "type"

    def __init__(self):
        super().__init__()
        self._background_threads = []

    @inject
    async def delete_document(
        self,
        identification: str,
        file_service: FileService = Depends(Provide[DependencyContainer.file_service]),
        rag_api: RagApi = Depends(Provide[DependencyContainer.rag_api]),
        key_value_store: FileStatusKeyValueStore = Depends(Provide[DependencyContainer.key_value_store]),
    ) -> None:
        error_messages = ""
        # Delete the document from file service and vector database
        logger.debug("Deleting existing document: %s", identification)
        try:
            key_value_store.remove(identification)
            file_service.delete_file(identification)
        except Exception as e:
            error_messages += "Error while deleting %s from file storage\n %s\n" % (identification, str(e))
        try:
            rag_api.remove_source_documents(
                DeleteRequest(metadata=[KeyValuePair(key="document", value=json.dumps(identification))])
            )
            logger.info("Deleted documents belonging to %s from rag.", identification)
        except Exception as e:
            error_messages += "Error while deleting %s from vector db\n%s" % (identification, str(e))
        if error_messages:
            raise HTTPException(404, error_messages)

    @inject
    async def get_all_documents(
        self,
        key_value_store: FileStatusKeyValueStore = Depends(Provide[DependencyContainer.key_value_store]),
    ) -> list[DocumentStatus]:
        all_documents = key_value_store.get_all()
        return [DocumentStatus(name=x[0], status=x[1]) for x in all_documents]

    @inject
    async def document_reference_id_get(
        self,
        identification: str,
        file_service: FileService = Depends(Provide[DependencyContainer.file_service]),
    ) -> Response:
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
                file_service.download_file(identification, document_buffer)
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

        if identification.endswith(".pdf"):
            media_type = "application/pdf"
        else:
            media_type = "application/octet-stream"

        headers = {
            "Content-Disposition": f'inline; filename="{identification}"',
            "Content-Type": media_type,
        }
        return Response(document_data, status_code=200, headers=headers, media_type=media_type)

    @inject
    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
        key_value_store: FileStatusKeyValueStore = Depends(Provide[DependencyContainer.key_value_store]),
    ) -> None:
        self._background_threads = [t for t in self._background_threads if t.is_alive()]
        content = await body.read()
        try:
            key_value_store.upsert(body.filename, Status.UPLOADING)
            thread = Thread(target=lambda: run(self._asave_new_document(content, body.filename, request)))
            thread.start()
            self._background_threads.append(thread)
        except ValueError as e:
            key_value_store.upsert(body.filename, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            key_value_store.upsert(body.filename, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @inject
    async def _asave_new_document(
        self,
        file_content: bytes,
        filename: str,
        request: Request,
        key_value_store: FileStatusKeyValueStore = Depends(Provide[DependencyContainer.key_value_store]),
    ):
        try:
            await self.delete_document(filename)
        except HTTPException as e:
            logger.error(
                "Error while trying to delete file %s before uploading %s. Still continuing with upload.", filename, e
            )
            key_value_store.upsert(filename, Status.ERROR)

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = Path(temp_dir) / filename
                with open(temp_file_path, "wb") as temp_file:
                    logger.debug("Temporary file created at %s.", temp_file_path)
                    temp_file.write(file_content)
                    logger.debug("Temp file created and content written.")
                    await self._aparse_document(Path(temp_file_path), request)
        except Exception as e:
            logger.error("Error during document parsing: %s %s", e, traceback.format_exc())
            key_value_store.upsert(filename, Status.ERROR)

    @inject
    async def _aparse_document(
        self,
        s3_file_path: Path,
        request: Request,
        document_extractor: ExtractorApi = Depends(Provide[DependencyContainer.document_extractor]),
        file_service: FileService = Depends(Provide[DependencyContainer.file_service]),
        rag_api: RagApi = Depends(Provide[DependencyContainer.rag_api]),
        information_enhancer: InformationEnhancer = Depends(Provide[DependencyContainer.information_enhancer]),
        information_mapper: InformationPiece2Document = Depends(Provide[DependencyContainer.information_mapper]),
        chunker: Chunker = Depends(Provide[DependencyContainer.chunker]),
        key_value_store: FileStatusKeyValueStore = Depends(Provide[DependencyContainer.key_value_store]),
    ):
        logger.debug("START parsing of the document %s", s3_file_path)
        filename = s3_file_path.name

        file_service.upload_file(s3_file_path, filename)
        key_value_store.upsert(filename, Status.PROCESSING)
        information_pieces = document_extractor.extract_information(ExtractionRequest(path_on_s3=filename))
        documents = [information_mapper.information_piece2document(x) for x in information_pieces]
        documents = await information_enhancer.ainvoke(documents)
        host_base_url = str(request.base_url)

        document_url = f"{host_base_url.rstrip('/')}/document_reference/{urllib.parse.quote_plus(filename)}"

        chunked_documents = chunker.chunk(documents)

        for idx, chunk in enumerate(chunked_documents):
            if chunk.metadata["id"] in chunk.metadata["related"]:
                chunk.metadata["related"].remove(chunk.metadata["id"])
            chunk.metadata.update(
                {
                    "chunk": idx,
                    "chunk_length": len(chunk.page_content),
                    "document_url": document_url,
                }
            )

        rag_api_documents = []
        for document in chunked_documents:
            metadata = [KeyValuePair(key=str(key), value=json.dumps(value)) for key, value in document.metadata.items()]
            content_type = ContentType(document.metadata[self.DOCUMENT_METADATA_TYPE_KEY].upper())
            rag_api_documents.append(
                UploadSourceDocument(
                    content_type=content_type,
                    metadata=metadata,
                    content=document.page_content,
                )
            )

        rag_api.upload_source_documents(rag_api_documents)
        key_value_store.upsert(filename, Status.READY)
        logger.info("File uploaded successfully: %s", filename)
