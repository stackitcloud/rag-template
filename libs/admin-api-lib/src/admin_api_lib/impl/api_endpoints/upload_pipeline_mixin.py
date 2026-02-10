"""Shared helpers for admin upload pipelines (file + source)."""

from __future__ import annotations

import asyncio
from contextlib import suppress

from langchain_core.documents import Document

from admin_api_lib.api_endpoints.document_deleter import DocumentDeleter
from admin_api_lib.chunker.chunker import Chunker
from admin_api_lib.impl.key_db.file_status_key_value_store import FileStatusKeyValueStore
from admin_api_lib.impl.mapper.informationpiece2document import InformationPiece2Document


class UploadCancelledError(Exception):
    """Raised when a running upload/ingestion was cancelled or became stale."""


class UploadPipelineMixin:
    """
    Mixin that consolidates shared pipeline steps for file and source uploads.

    The concrete uploader must provide these attributes:
    - `_key_value_store: FileStatusKeyValueStore`
    - `_document_deleter: DocumentDeleter`
    - `_information_mapper: InformationPiece2Document`
    - `_chunker: Chunker`
    """

    _key_value_store: FileStatusKeyValueStore
    _document_deleter: DocumentDeleter
    _information_mapper: InformationPiece2Document
    _chunker: Chunker

    def _assert_not_cancelled(self, identification: str, run_id: str) -> None:
        if self._key_value_store.is_cancelled_or_stale(identification, run_id):
            raise UploadCancelledError(f"Upload cancelled for {identification}")

    def _map_information_pieces(self, information_pieces: list) -> list[Document]:
        """Map extractor information pieces to langchain documents."""
        return [self._information_mapper.extractor_information_piece2document(piece) for piece in information_pieces]

    async def _achunk_documents(self, documents: list[Document]) -> list[Document]:
        """Chunk documents using the configured chunker in a thread pool."""
        return await asyncio.to_thread(self._chunker.chunk, documents)

    async def _abest_effort_replace_existing(self, identification: str) -> None:
        """Best-effort delete of existing document chunks to support re-upload."""
        with suppress(Exception):
            await self._document_deleter.adelete_document(
                identification,
                remove_from_key_value_store=False,
                remove_from_storage=False,
            )

    async def _abest_effort_cleanup_cancelled(self, identification: str) -> None:
        """Best-effort cleanup for cancelled uploads (status + vector-db artifacts)."""
        with suppress(Exception):
            await self._document_deleter.adelete_document(
                identification,
                remove_from_key_value_store=False,
                remove_from_storage=False,
            )
        with suppress(Exception):
            self._key_value_store.remove(identification)
