import logging
import tempfile
import traceback
import urllib
from asyncio import run
from pathlib import Path
from threading import Thread

from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.api_endpoints.document_uploader import DocumentUploader
from admin_api_lib.extractor_api_client.openapi_client.api.extractor_api import ExtractorApi
from admin_api_lib.extractor_api_client.openapi_client.models.extraction_request import ExtractionRequest
from admin_api_lib.file_services.file_service import FileService
from admin_api_lib.impl.chunker.chunker import Chunker
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_api_lib.information_enhancer.information_enhancer import InformationEnhancer
from admin_api_lib.models.status import Status
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from fastapi import HTTPException, Request, UploadFile, status

logger = logging.getLogger(__name__)


class DefaultDocumentUploader(DocumentUploader):
    def __init__(
        self,
        document_extractor: ExtractorApi,
        file_service: FileService,
        rag_api: RagApi,
        information_enhancer: InformationEnhancer,
        information_mapper: InformationPiece2Document,
        chunker: Chunker,
        key_value_store: FileStatusKeyValueStore,
        document_deleter: DocumentDeleter,
    ):
        self._document_extractor = document_extractor
        self._file_service = file_service
        self._rag_api = rag_api
        self._information_enhancer = information_enhancer
        self._information_mapper = information_mapper
        self._chunker = chunker
        self._key_value_store = key_value_store
        self._document_deleter = document_deleter
        self._background_threads = []

    async def aupload_documents_post(
        self,
        body: UploadFile,
        request: Request,
    ) -> None:
        self._background_threads = [t for t in self._background_threads if t.is_alive()]
        content = await body.read()
        try:
            self._key_value_store.upsert(body.filename, Status.UPLOADING)
            thread = Thread(target=lambda: run(self._asave_new_document(content, body.filename, request)))
            thread.start()
            self._background_threads.append(thread)
        except ValueError as e:
            self._key_value_store.upsert(body.filename, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self._key_value_store.upsert(body.filename, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def _asave_new_document(
        self,
        file_content: bytes,
        filename: str,
        request: Request,
    ):
        try:
            await self._document_deleter.adelete_document(filename)
        except HTTPException as e:
            logger.error(
                "Error while trying to delete file %s before uploading %s. Still continuing with upload.", filename, e
            )
            self._key_value_store.upsert(filename, Status.ERROR)

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
            self._key_value_store.upsert(filename, Status.ERROR)

    async def _aparse_document(
        self,
        s3_file_path: Path,
        request: Request,
    ):
        logger.debug("START parsing of the document %s", s3_file_path)
        filename = s3_file_path.name

        self._file_service.upload_file(s3_file_path, filename)
        self._key_value_store.upsert(filename, Status.PROCESSING)

        information_pieces = self._document_extractor.extract_from_file_post(ExtractionRequest(path_on_s3=filename))
        documents = [self._information_mapper.extractor_information_piece2document(x) for x in information_pieces]
        host_base_url = str(request.base_url)
        document_url = f"{host_base_url.rstrip('/')}/document_reference/{urllib.parse.quote_plus(filename)}"

        chunked_documents = self._chunker.chunk(documents)

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

        enhanced_documents = await self._information_enhancer.ainvoke(chunked_documents)
        rag_information_pieces = [
            self._information_mapper.document2rag_information_piece(doc) for doc in enhanced_documents
        ]

        self._rag_api.upload_information_piece(rag_information_pieces)
        self._key_value_store.upsert(filename, Status.READY)
        logger.info("File uploaded successfully: %s", filename)
