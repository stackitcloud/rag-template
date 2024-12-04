from asyncio import run
import logging
from threading import Thread
from fastapi import status

from admin_api_lib.api_endpoints.confluence_loader import ConfluenceLoader
from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.extractor_api_client.openapi_client.api.extractor_api import ExtractorApi
from admin_api_lib.chunker.chunker import Chunker
from admin_api_lib.impl.mapper.confluence_settings_mapper import ConfluenceSettingsMapper
from admin_api_lib.information_enhancer.information_enhancer import InformationEnhancer
from admin_api_lib.rag_backend_client.openapi_client.api.rag_api import RagApi
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.impl.settings.confluence_settings import ConfluenceSettings
from admin_api_lib.impl.mapper.informationpiece2document import InformationPiece2Document
from admin_api_lib.models.status import Status
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class DefaultConfluenceLoader(ConfluenceLoader):
    CONFLUENCE_SPACE = "confluence_space"

    def __init__(
        self,
        extractor_api: ExtractorApi,
        settings: ConfluenceSettings,
        information_mapper: InformationPiece2Document,
        rag_api: RagApi,
        key_value_store: FileStatusKeyValueStore,
        information_enhancer: InformationEnhancer,
        chunker: Chunker,
        document_deleter: DocumentDeleter,
        settings_mapper: ConfluenceSettingsMapper,
    ):
        self._extractor_api = extractor_api
        self._rag_api = rag_api
        self._settings = settings
        self._key_value_store = key_value_store
        self._information_mapper = information_mapper
        self._information_enhancer = information_enhancer
        self._chunker = chunker
        self._document_deleter = document_deleter
        self._settings_mapper = settings_mapper
        self._background_thread = None

    async def aload_from_confluence(self) -> None:
        """
        Asynchronously loads content from Confluence using the configured settings.
        """
        if not (
            self._settings.url
            and self._settings.url.strip()
            and self._settings.space_key
            and self._settings.space_key.strip()
            and self._settings.token
            and self._settings.token.strip()
        ):
            raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "The confluence loader is not configured!")

        if self._background_thread is not None and self._background_thread.is_alive():
            raise HTTPException(
                status.HTTP_423_LOCKED, "Confluence loader is locked... Please wait for the current load to finish."
            )
        self._background_thread = Thread(target=lambda: run(self._aload_from_confluence()))
        self._background_thread.start()

    async def _aload_from_confluence(self) -> None:
        params = self._settings_mapper.map_settings_to_params(self._settings)
        try:
            self._key_value_store.upsert(self._settings.url, Status.PROCESSING)
            information_pieces = self._extractor_api.extract_from_confluence_post(params)
            documents = [self._information_mapper.extractor_information_piece2document(x) for x in information_pieces]
            chunked_documents = self._chunker.chunk(documents)
            rag_information_pieces = [
                self._information_mapper.document2rag_information_piece(doc) for doc in chunked_documents
            ]
        except Exception as e:
            self._key_value_store.upsert(self._settings.url, Status.ERROR)
            logger.error("Error while loading from Confluence: %s", str(e))
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error loading from Confluence: {str(e)}"
            ) from e

        await self._delete_previous_information_pieces()
        self._key_value_store.upsert(self._settings.url, Status.UPLOADING)
        self._upload_information_pieces(rag_information_pieces)

    async def _delete_previous_information_pieces(self):
        try:
            await self._document_deleter.adelete_document(self._settings.url)
        except HTTPException as e:
            logger.error(
                (
                    "Error while trying to delete documents with id: %s before uploading %s."
                    "NOTE: Still continuing with upload."
                ),
                self._settings.url,
                e,
            )

    def _upload_information_pieces(self, rag_api_documents):
        try:
            self._rag_api.upload_information_piece(rag_api_documents)
            self._key_value_store.upsert(self._settings.url, Status.READY)
            logger.info("Confluence loaded successfully")
        except Exception as e:
            self._key_value_store.upsert(self._settings.url, Status.ERROR)
            logger.error("Error while uploading Confluence to the database: %s", str(e))
            raise HTTPException(500, f"Error loading from Confluence: {str(e)}") from e
