"""Module containing the MarkitdownFileExtractor."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from markitdown import MarkItDown

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece

logger = logging.getLogger(__name__)


class MarkitdownFileExtractor(InformationFileExtractor):
    """InformationFileExtractor implementation powered by MarkItDown."""

    def __init__(self, file_service: FileService):
        super().__init__(file_service)
        self._converter = MarkItDown()

    @property
    def compatible_file_types(self) -> list[FileType]:
        """Return the list of file types handled by this extractor."""
        return [
            FileType.PDF,
            FileType.DOCX,
            FileType.PPTX,
            FileType.XML,
            FileType.EPUB,
            FileType.HTML,
        ]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        with file_path.open("rb") as stream:
            result = self._converter.convert_stream(stream, filename=file_path.name)

        markdown = self._extract_markdown(result)
        if not markdown:
            logger.info("MarkItDown returned no markdown for file: %s", file_path)
            return []

        pieces = [
            self._create_information_piece(
                document_name=name,
                page=1,
                content=markdown,
                content_type=ContentType.TEXT,
                additional_meta={"origin_extractor": "markitdown"},
            )
        ]

        for idx, table_markdown in enumerate(self._extract_markdown_tables(markdown), start=1):
            pieces.append(
                self._create_information_piece(
                    document_name=name,
                    page=1,
                    content=table_markdown,
                    content_type=ContentType.TABLE,
                    additional_meta={
                        "origin_extractor": "markitdown",
                        "table_index": idx,
                    },
                )
            )

        return pieces

    @staticmethod
    def _extract_markdown(result: object) -> str:
        if result is None:
            return ""
        if hasattr(result, "text") and getattr(result, "text"):
            return getattr(result, "text")
        if hasattr(result, "markdown") and getattr(result, "markdown"):
            return getattr(result, "markdown")
        return str(result) if isinstance(result, str) else ""

    def _extract_markdown_tables(self, markdown: str) -> list[str]:
        tables: list[str] = []
        buffer: list[str] = []

        for line in markdown.splitlines():
            if self._is_table_line(line):
                buffer.append(line)
                continue
            self._flush_table_buffer(buffer, tables)

        self._flush_table_buffer(buffer, tables)
        return tables

    @staticmethod
    def _is_table_line(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        pipe_count = stripped.count("|")
        return pipe_count >= 2 and not stripped.startswith("```")

    @staticmethod
    def _flush_table_buffer(buffer: list[str], tables: list[str]) -> None:
        if not buffer:
            return
        has_separator = any("---" in row for row in buffer[1:3])
        if has_separator:
            table = "\n".join(buffer).strip()
            if table:
                tables.append(table)
        buffer.clear()

    def _create_information_piece(
        self,
        document_name: str,
        page: int,
        content: str,
        content_type: ContentType,
        additional_meta: dict[str, Any] | None = None,
    ) -> InternalInformationPiece:
        metadata = {
            "document": document_name,
            "page": page,
            "id": hash_datetime(),
            "related": [],
        }
        if additional_meta:
            metadata.update(additional_meta)

        return InternalInformationPiece(
            type=content_type,
            metadata=metadata,
            page_content=content,
        )
