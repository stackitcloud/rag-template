"""Module containing the DoclingFileExtractor."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from docling.document_converter import (
    DocumentConverter,
    ExcelFormatOption,
    ImageFormatOption,
    InputFormat,
    PdfFormatOption,
    PowerpointFormatOption,
    WordFormatOption,
)

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece

logger = logging.getLogger(__name__)


class DoclingFileExtractor(InformationFileExtractor):
    """InformationFileExtractor implemented with Docling."""

    def __init__(self, file_service: FileService):
        super().__init__(file_service)
        format_options = {
            InputFormat.PDF: PdfFormatOption(ocr=True),
            InputFormat.IMAGE: ImageFormatOption(ocr=True),
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.XLSX: ExcelFormatOption(),
        }
        html_format = getattr(InputFormat, "HTML", None)
        if html_format:
            format_options[html_format] = None
        self._converter = DocumentConverter(format_options=format_options)

    @property
    def compatible_file_types(self) -> list[FileType]:
        """Return supported file types."""
        return [
            FileType.PDF,
            FileType.DOCX,
            FileType.PPTX,
            FileType.XLSX,
            FileType.HTML,
        ]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        result = self._converter.convert(file_path)
        document = result.document

        pieces: list[InternalInformationPiece] = []
        for block in getattr(document, "text_blocks", []):
            text = getattr(block, "text", "")
            if not text:
                continue
            page_number = self._resolve_page_number(block)
            pieces.append(
                self._create_information_piece(
                    document_name=name,
                    page=page_number,
                    content=text,
                    content_type=ContentType.TEXT,
                    additional_meta={"origin_extractor": "docling"},
                )
            )

        for table_index, table in enumerate(getattr(document, "tables", []), start=1):
            serialized_table = self._serialize_table(table)
            if not serialized_table:
                continue
            page_number = self._resolve_page_number(table)
            pieces.append(
                self._create_information_piece(
                    document_name=name,
                    page=page_number,
                    content=serialized_table,
                    content_type=ContentType.TABLE,
                    additional_meta={
                        "origin_extractor": "docling",
                        "table_index": table_index,
                    },
                )
            )

        return pieces

    @staticmethod
    def _resolve_page_number(block: Any) -> int:
        for attr in ("page_no", "page_number", "page"):
            page_number = getattr(block, attr, None)
            if isinstance(page_number, int):
                return page_number
        return 1

    def _serialize_table(self, table: Any) -> str:
        if hasattr(table, "to_markdown"):
            try:
                markdown = table.to_markdown()
                if markdown:
                    return markdown
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug("Docling table markdown conversion failed: %s", exc)

        rows = self._normalize_rows(table)
        if not rows:
            return ""
        column_count = max(len(row) for row in rows)
        padded_rows = [row + [""] * (column_count - len(row)) for row in rows]
        header = padded_rows[0]
        separator = ["---"] * column_count
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        for row in padded_rows[1:]:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)

    @staticmethod
    def _normalize_rows(table: Any) -> list[list[str]]:
        candidates = getattr(table, "rows", None) or getattr(table, "cells", None) or getattr(table, "data", None)
        if candidates is None:
            return []

        normalized: list[list[str]] = []
        for row in candidates:
            cells = getattr(row, "cells", None) or row
            row_values: list[str] = []
            for cell in cells:
                row_values.append(DoclingFileExtractor._cell_to_text(cell))
            normalized.append(row_values)
        return normalized

    @staticmethod
    def _cell_to_text(cell: Any) -> str:
        for attr in ("text", "value", "content", "plain_text"):
            if hasattr(cell, attr):
                text_candidate = DoclingFileExtractor._stringify_cell_value(getattr(cell, attr))
                if text_candidate:
                    return text_candidate

        getter = getattr(cell, "get_text", None)
        if callable(getter):
            try:
                text_candidate = DoclingFileExtractor._stringify_cell_value(getter())
                if text_candidate:
                    return text_candidate
            except Exception:  # pragma: no cover - defensive logging
                logger.debug("Docling cell get_text invocation failed", exc_info=True)

        cell_repr = str(cell).strip()
        match = re.search(r"text\s*=\s*(['\"])(.*?)\1", cell_repr, re.DOTALL)
        if match:
            return match.group(2).strip()

        if isinstance(cell, (list, tuple)):
            return " ".join(part for part in (DoclingFileExtractor._cell_to_text(item) for item in cell) if part)

        return cell_repr

    @staticmethod
    def _stringify_cell_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (list, tuple, set)):
            return " ".join(
                part for part in (DoclingFileExtractor._stringify_cell_value(item) for item in value) if part
            )
        return str(value).strip()

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
