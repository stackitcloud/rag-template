"""Module for the default source uploader implementation."""

import logging
import asyncio
from threading import Thread
from contextlib import suppress

from pydantic import StrictStr
from fastapi import status, HTTPException

from admin_api_lib.extractor_api_client.openapi_client.api.extractor_api import ExtractorApi
from admin_api_lib.extractor_api_client.openapi_client.models.extraction_parameters import ExtractionParameters
from admin_api_lib.impl.settings.source_uploader_settings import SourceUploaderSettings
from admin_api_lib.models.key_value_pair import KeyValuePair
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.api_endpoints.source_uploader import SourceUploader
from admin_api_lib.chunker.chunker import Chunker
from admin_api_lib.models.status import Status
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.impl.api_endpoints.upload_pipeline_mixin import (
    UploadCancelledError,
    UploadPipelineMixin,
)
from admin_api_lib.information_enhancer.information_enhancer import InformationEnhancer
from admin_api_lib.utils.utils import sanitize_document_name

logger = logging.getLogger(__name__)


class DefaultSourceUploader(UploadPipelineMixin, SourceUploader):
    """The DefaultSourceUploader is responsible for uploading source files for content extraction."""

    def __init__(
        self,
        extractor_api: ExtractorApi,
        key_value_store: FileStatusKeyValueStore,
        information_enhancer: InformationEnhancer,
        chunker: Chunker,
        document_deleter: DocumentDeleter,
        rag_api: RagApi,
        information_mapper: InformationPiece2Document,
        settings: SourceUploaderSettings,
    ):
        """
        Initialize the DefaultSourceUploader.

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
        """
        super().__init__()
        self._extractor_api = extractor_api
        self._rag_api = rag_api
        self._key_value_store = key_value_store
        self._information_mapper = information_mapper
        self._information_enhancer = information_enhancer
        self._chunker = chunker
        self._document_deleter = document_deleter
        self._background_threads = []
        self._settings = settings

    def cancel_upload(self, identification: str) -> None:
        """Mark an in-flight source upload as cancelled."""
        self._key_value_store.cancel_run(identification)
        logger.info("Cancellation requested for source upload: %s", identification)

    async def upload_source(
        self,
        source_type: StrictStr,
        name: StrictStr,
        kwargs: list[KeyValuePair],
    ) -> None:
        """
        Upload the parameters for source content extraction.

        Parameters
        ----------
        source_type : str
            The type of the source. Is used by the extractor service to determine the correct extraction method.
        name : str
            Display name of the source.
        kwargs : list[KeyValuePair]
            List of KeyValuePair with parameters used for the extraction.
        timeout : float, optional
            Timeout for the operation, by default 3600.0 seconds (1 hour).

        Returns
        -------
        None
        """
        self._prune_background_threads()

        source_name = f"{source_type}:{sanitize_document_name(name)}"
        run_id: str | None = None
        thread_started = False
        try:
            self._check_if_already_in_processing(source_name)
            run_id = self._key_value_store.start_run(source_name)
            self._key_value_store.upsert(source_name, Status.PROCESSING)

            thread = Thread(
                target=self._thread_worker,
                args=(source_name, source_type, kwargs, self._settings.timeout, run_id),
            )
            thread.start()
            self._background_threads.append(thread)
            thread_started = True
        except ValueError as e:
            self._key_value_store.upsert(source_name, Status.ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            self._key_value_store.upsert(source_name, Status.ERROR)
            logger.exception("Error while uploading %s", source_name)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        finally:
            if run_id is not None and not thread_started:
                self._key_value_store.finish_run(source_name, run_id)

    def _check_if_already_in_processing(self, source_name: str) -> None:
        """
        Check if the source is already in processing state.

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

    async def _aextract_information_pieces(
        self,
        source_name: str,
        source_type: StrictStr,
        kwargs: list[KeyValuePair],
    ) -> list:
        """Extract information pieces for a source from the extractor service."""
        information_pieces = await asyncio.to_thread(
            self._extractor_api.extract_from_source,
            ExtractionParameters(
                source_type=source_type, document_name=source_name, kwargs=[x.to_dict() for x in kwargs]
            ),
        )
        if not information_pieces:
            logger.error("No information pieces found in the document: %s", source_name)
            raise RuntimeError("No information pieces found")
        return information_pieces

    def _thread_worker(self, source_name, source_type, kwargs, timeout, run_id: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                asyncio.wait_for(
                    self._handle_source_upload(
                        source_name=source_name,
                        source_type=source_type,
                        kwargs=kwargs,
                        run_id=run_id,
                    ),
                    timeout=timeout,
                )
            )
        except asyncio.TimeoutError:
            if self._key_value_store.is_cancelled_or_stale(source_name, run_id):
                logger.info("Timed out worker for %s ignored because upload was cancelled.", source_name)
                return
            logger.error(
                "Upload of %s timed out after %s seconds (increase SOURCE_UPLOADER_TIMEOUT to allow longer ingestions)",
                source_name,
                timeout,
            )
            self._key_value_store.upsert(source_name, Status.ERROR)
        except Exception:
            if self._key_value_store.is_cancelled_or_stale(source_name, run_id):
                logger.info("Worker exception for %s ignored because upload was cancelled.", source_name)
                return
            logger.exception("Error while uploading %s", source_name)
            self._key_value_store.upsert(source_name, Status.ERROR)
        finally:
            loop.close()
            self._key_value_store.finish_run(source_name, run_id)

    async def _handle_source_upload(
        self,
        source_name: str,
        source_type: StrictStr,
        kwargs: list[KeyValuePair],
        run_id: str | None = None,
    ):
        try:
            if run_id is None:
                run_id = self._key_value_store.start_run(source_name)
            self._assert_not_cancelled(source_name, run_id)
            information_pieces = await self._aextract_information_pieces(source_name, source_type, kwargs)
            self._assert_not_cancelled(source_name, run_id)

            documents = self._map_information_pieces(information_pieces)
            chunked_documents = await self._achunk_documents(documents)
            self._assert_not_cancelled(source_name, run_id)

            # limit concurrency to avoid spawning multiple threads per call
            enhanced_documents = await self._information_enhancer.ainvoke(
                chunked_documents, config={"max_concurrency": 1}
            )
            self._assert_not_cancelled(source_name, run_id)

            rag_information_pieces = [
                self._information_mapper.document2rag_information_piece(doc) for doc in enhanced_documents
            ]

            await self._abest_effort_replace_existing(source_name)

            self._assert_not_cancelled(source_name, run_id)
            # Run blocking RAG API call in thread pool to avoid blocking event loop
            await asyncio.to_thread(self._rag_api.upload_information_piece, rag_information_pieces)

            if self._key_value_store.is_cancelled_or_stale(source_name, run_id):
                await self._abest_effort_cleanup_cancelled(source_name)
                logger.info("Upload for %s finished after cancellation request; cleaned up artifacts.", source_name)
                return

            self._key_value_store.upsert(source_name, Status.READY)
            logger.info("Source uploaded successfully: %s", source_name)
        except UploadCancelledError:
            with suppress(Exception):
                self._key_value_store.remove(source_name)
            logger.info("Upload cancelled for %s.", source_name)
        except Exception:
            if self._key_value_store.is_cancelled_or_stale(source_name, run_id):
                logger.info("Upload for %s stopped because cancellation was requested.", source_name)
                return
            self._key_value_store.upsert(source_name, Status.ERROR)
            logger.exception("Error while uploading %s", source_name)
        finally:
            # Best-effort cleanup for direct calls/tests; thread worker also calls finish_run.
            if run_id is not None:
                self._key_value_store.finish_run(source_name, run_id)
