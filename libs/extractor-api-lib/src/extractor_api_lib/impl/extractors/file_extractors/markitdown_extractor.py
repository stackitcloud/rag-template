"""Module for MarkItDown-based file extraction."""

import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable

from markdown_it import MarkdownIt
from markitdown import MarkItDown
from pypdf import PdfReader, PdfWriter

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import (
    InternalInformationPiece,
)

logger = logging.getLogger(__name__)


class MarkitdownFileExtractor(InformationFileExtractor):
    """InformationFileExtractor implementation powered by MarkItDown."""

    # MarkItDown's PPTX converter annotates slides like:
    # <!-- Slide number: 3 -->
    SLIDE_MARKER_RE = re.compile(r"<!--\s*Slide number:\s*(\d+)\s*-->")

    def __init__(self, file_service: FileService):
        """Initialize the MarkitdownFileExtractor with the given FileService.

        Parameters
        ----------
        file_service : FileService
            The file service to use for file operations.
        """
        super().__init__(file_service)
        self._converter = MarkItDown()
        self._md_table_parser = MarkdownIt("commonmark").enable("table")

    @property
    def compatible_file_types(self) -> list[FileType]:
        """Return the list of file types handled by this extractor.

        Returns
        -------
        list[FileType]
            The list of file types handled by this extractor.
        """
        return [
            FileType.PDF,
            FileType.DOCX,
            FileType.PPTX,
            FileType.EPUB,
            FileType.HTML,
            FileType.CSV,
            FileType.TXT,
        ]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """Asynchronously extract content from a file using MarkItDown.

        Parameters
        ----------
        file_path : Path
            The path to the file.
        name : str
            The name of the document.

        Returns
        -------
        list[InternalInformationPiece]
            The list of extracted information pieces.
        """

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf_pages(file_path, name)

        with file_path.open("rb") as stream:
            result = self._converter.convert_stream(stream, filename=file_path.name)

        markdown = self._extract_markdown(result)
        if not markdown:
            logger.info("MarkItDown returned no markdown for file: %s", file_path)
            return []

        # --- PPTX: split by slide markers -----------------------------------
        if suffix == ".pptx":
            return self._extract_pptx_pages(document_name=name, markdown=markdown)

        # --- DOCX, EPUB, HTML, CSV, TXT: single logical page ----------------
        return list(
            self._build_pieces_for_markdown(
                document_name=name,
                page=1,
                markdown=markdown,
            )
        )

    # ------------------------------------------------------------------ utils

    @staticmethod
    def _extract_markdown(result: object) -> str:
        """Robustly grab markdown from a DocumentConverterResult or string."""
        if result is None:
            return ""

        # Newer MarkItDown prefers `.markdown`; `.text_content` is kept for BC.
        for attr in ("markdown", "text_content", "text"):
            value = getattr(result, attr, None)
            if isinstance(value, str) and value.strip():
                return value

        if isinstance(result, str):
            return result

        return ""

    def _extract_markdown_tables(self, markdown: str) -> list[str]:
        """Use markdown-it-py to extract table blocks as markdown slices."""
        if not markdown:
            return []

        lines = markdown.splitlines()
        tokens = self._md_table_parser.parse(markdown)

        tables: list[str] = []
        for token in tokens:
            if token.type == "table_open" and token.map:
                start_line, end_line = token.map
                start_line = max(0, start_line)
                end_line = min(len(lines), end_line)
                if start_line >= end_line:
                    continue

                table_src = "\n".join(lines[start_line:end_line]).strip()
                if table_src:
                    tables.append(table_src)

        return tables

    def _build_pieces_for_markdown(
        self,
        document_name: str,
        page: int,
        markdown: str,
    ) -> Iterable[InternalInformationPiece]:
        """Create one TEXT + N TABLE pieces for the given markdown block."""
        if not markdown:
            return []

        pieces: list[InternalInformationPiece] = []

        # Full-page text
        pieces.append(
            self._create_information_piece(
                document_name=document_name,
                page=page,
                content=markdown,
                content_type=ContentType.TEXT,
                additional_meta={"origin_extractor": "markitdown"},
            )
        )

        # Page-level tables
        for idx, table_markdown in enumerate(self._extract_markdown_tables(markdown), start=1):
            pieces.append(
                self._create_information_piece(
                    document_name=document_name,
                    page=page,
                    content=table_markdown,
                    content_type=ContentType.TABLE,
                    additional_meta={
                        "origin_extractor": "markitdown",
                        "table_index": idx,
                    },
                )
            )

        return pieces

    # -------------------------------------------------------------- PDF pages

    def _extract_pdf_pages(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """Split the PDF and run MarkItDown once per page.

        This ensures that the page number is preserved in the extracted pieces.

        Parameters
        ----------
        file_path : Path
            The path to the PDF file.
        name : str
            The name of the document.
        """
        reader = PdfReader(str(file_path))
        pieces: list[InternalInformationPiece] = []

        for page_index, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            buf = BytesIO()
            writer.write(buf)
            buf.seek(0)

            result = self._converter.convert_stream(
                buf,
                filename=f"{file_path.name}-page-{page_index}.pdf",
            )
            markdown = self._extract_markdown(result)
            if not markdown:
                logger.debug("Empty markdown for %s page %s", file_path, page_index)
                continue

            pieces.extend(
                self._build_pieces_for_markdown(
                    document_name=name,
                    page=page_index,
                    markdown=markdown,
                )
            )

        if not pieces:
            logger.info("No content extracted from PDF: %s", file_path)

        return pieces

    # ------------------------------------------------------------- PPTX pages

    def _extract_pptx_pages(self, document_name: str, markdown: str) -> list[InternalInformationPiece]:
        """Split PPTX markdown by slide comments and tag pieces with slide number."""
        slides = self._split_pptx_markdown(markdown)
        pieces: list[InternalInformationPiece] = []

        for page, slide_markdown in slides:
            pieces.extend(
                self._build_pieces_for_markdown(
                    document_name=document_name,
                    page=page,
                    markdown=slide_markdown,
                )
            )

        return pieces

    def _split_pptx_markdown(self, markdown: str) -> list[tuple[int, str]]:
        """
        Split PPTX-converted markdown into (slide_number, markdown_chunk).

        Relies on MarkItDown's `<!-- Slide number: N -->` comments, which are
        part of the PPTX converter output and commonly used for slide-wise RAG.
        """
        matches = list(self.SLIDE_MARKER_RE.finditer(markdown))
        if not matches:
            cleaned = markdown.strip()
            return [(1, cleaned)] if cleaned else []

        slides: list[tuple[int, str]] = []
        for i, match in enumerate(matches):
            slide_no = int(match.group(1))
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            chunk = markdown[start:end].strip()
            if chunk:
                slides.append((slide_no, chunk))

        return slides

    # -------------------------------------------------------------- piece ctor

    def _create_information_piece(
        self,
        document_name: str,
        page: int,
        content: str,
        content_type: ContentType,
        additional_meta: dict[str, Any] | None = None,
    ) -> InternalInformationPiece:
        metadata: dict[str, Any] = {
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
