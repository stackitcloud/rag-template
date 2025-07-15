import logging
from pathlib import Path
import traceback
import urllib
import tempfile
import asyncio
from contextlib import suppress

from fastapi import UploadFile, status, HTTPException
from langchain_core.documents import Document

from admin_api_lib.file_services.file_service import FileService
from admin_api_lib.extractor_api_client.openapi_client.models.extraction_request import ExtractionRequest
from admin_api_lib.api_endpoints.file_uploader import FileUploader
from admin_api_lib.extractor_api_client.openapi_client.api.extractor_api import ExtractorApi
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.chunker.chunker import Chunker
from admin_api_lib.models.status import Status
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.information_enhancer.information_enhancer import InformationEnhancer
from admin_api_lib.utils.utils import sanitize_document_name

logger = logging.getLogger(__name__)


class DefaultFileUploader(FileUploader):
    """The DefaultFileUploader is responsible for adding a new source file document to the available content."""

    def __init__(
        self,
        extractor_api: ExtractorApi,
        key_value_store: FileStatusKeyValueStore,
        information_enhancer: InformationEnhancer,
        chunker: Chunker,
        document_deleter: DocumentDeleter,
        rag_api: RagApi,
        information_mapper: InformationPiece2Document,
        file_service: FileService,
    ):
        """
        Initialize the DefaultFileUploader.

        Parameters
        ----------
        extractor_api : ExtractorApi
            Client for the Extraction service.
        key_value_store : FileStatusKeyValueStore
            The key-value store for storing filename and the corresponding status.
        information_enhancer : InformationEnhancer
            The service for enhancing information.
        chunker : Chunker
            The service for chunking documents into chunks.
        document_deleter : DocumentDeleter
            The service for deleting documents.
        rag_api : RagApi
            The API for RAG backend.
        information_mapper : InformationPiece2Document
            The mapper for converting information pieces to langchain documents.
        file_service : FileService
            The service for handling file operations on the S3 storage
        """
        super().__init__()
        self._extractor_api = extractor_api
        self._rag_api = rag_api
        self._key_value_store = key_value_store
        self._information_mapper = information_mapper
        self._information_enhancer = information_enhancer
        self._chunker = chunker
        self._document_deleter = document_deleter
        self._background_tasks = []
        self._file_service = file_service

    async def upload_file(
        self,
        base_url: str,
        file: UploadFile,
    ) -> None:
        """
        Uploads a source file for content extraction.

        Parameters
        ----------
        base_url : str
            The base url of the service. Is used to determine the download link of the file.
        file : UploadFile
            The file to process.

        Returns
        -------
        None
        """
        self._prune_background_tasks()

        try:
            file.filename = sanitize_document_name(file.filename)
            source_name = f"file:{sanitize_document_name(file.filename)}"
            self._check_if_already_in_processing(source_name)
            self._key_value_store.upsert(source_name, Status.PROCESSING)
            content = await file.read()
            s3_path = await self._asave_new_document(content, file.filename, source_name)

            task = asyncio.create_task(self._handle_source_upload(s3_path, source_name, file.filename, base_url))
            task.add_done_callback(self._log_task_exception)
            self._background_tasks.append(task)
        except ValueError as e:
            self._key_value_store.upsert(source_name, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self._key_value_store.upsert(source_name, Status.ERROR)
            logger.error("Error while uploading %s = %s", source_name, str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def _log_task_exception(self, task: asyncio.Task) -> None:
        """
        Log exceptions from completed background tasks.

        Parameters
        ----------
        task : asyncio.Task
            The completed task to check for exceptions.
        """
        if task.done() and not task.cancelled():
            try:
                task.result()  # This will raise the exception if one occurred
            except Exception as e:
                logger.error("Background task failed with exception: %s", str(e))
                logger.debug("Background task exception traceback: %s", traceback.format_exc())

    def _prune_background_tasks(self) -> None:
        """
        Remove completed background tasks from the list.
        """
        self._background_tasks = [task for task in self._background_tasks if not task.done()]

    def _check_if_already_in_processing(self, source_name: str) -> None:
        """
        Checks if the source is already in processing state.

        Parameters
        ----------
        source_name : str
            The name of the source.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the source is already in processing state.
        """
        existing = [s for name, s in self._key_value_store.get_all() if name == source_name]
        if any(s == Status.PROCESSING for s in existing):
            raise ValueError(f"Document {source_name} is already in processing state")

    async def _handle_source_upload(
        self,
        s3_path: Path,
        source_name: str,
        file_name: str,
        base_url: str,
    ):
        try:
            # Run blocking extractor API call in thread pool to avoid blocking event loop
            information_pieces = await asyncio.to_thread(
                self._extractor_api.extract_from_file_post,
                ExtractionRequest(path_on_s3=str(s3_path), document_name=source_name),
            )

            if not information_pieces:
                self._key_value_store.upsert(source_name, Status.ERROR)
                logger.error("No information pieces found in the document: %s", source_name)
                raise Exception("No information pieces found")
            documents: list[Document] = []
            for piece in information_pieces:
                documents.append(self._information_mapper.extractor_information_piece2document(piece))

            # Run blocking chunker call in thread pool to avoid blocking event loop
            chunked_documents = await asyncio.to_thread(self._chunker.chunk, documents)

            enhanced_documents = await self._information_enhancer.ainvoke(chunked_documents)
            self._add_file_url(file_name, base_url, enhanced_documents)

            rag_information_pieces = [
                self._information_mapper.document2rag_information_piece(doc) for doc in enhanced_documents
            ]
            # Replace old document
            # deletion is allowed to fail
            with suppress(Exception):
                await self._document_deleter.adelete_document(source_name, remove_from_key_value_store=False)

            # Run blocking RAG API call in thread pool to avoid blocking event loop
            await asyncio.to_thread(self._rag_api.upload_information_piece, rag_information_pieces)
            self._key_value_store.upsert(source_name, Status.READY)
            logger.info("Source uploaded successfully: %s", source_name)
        except Exception as e:
            self._key_value_store.upsert(source_name, Status.ERROR)
            logger.error("Error while uploading %s = %s", source_name, str(e))

    def _add_file_url(self, file_name: str, base_url: str, chunked_documents: list[Document]):
        document_url = f"{base_url.rstrip('/')}/document_reference/{urllib.parse.quote_plus(file_name)}"
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

    async def _asave_new_document(
        self,
        file_content: bytes,
        filename: str,
        source_name: str,
    ) -> Path:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = Path(temp_dir) / filename
                with open(temp_file_path, "wb") as temp_file:
                    logger.debug("Temporary file created at %s.", temp_file_path)
                    temp_file.write(file_content)
                    logger.debug("Temp file created and content written.")

                self._file_service.upload_file(Path(temp_file_path), filename)
                return filename
        except Exception as e:
            logger.error("Error during document saving: %s %s", e, traceback.format_exc())
            self._key_value_store.upsert(source_name, Status.ERROR)
