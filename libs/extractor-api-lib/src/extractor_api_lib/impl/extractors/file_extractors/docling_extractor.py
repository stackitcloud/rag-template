"""Module for Docling file extraction."""

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from docling.document_converter import (
    ConversionResult,
    DocumentConverter,
    ExcelFormatOption,
    ImageFormatOption,
    InputFormat,
    PdfFormatOption,
    PowerpointFormatOption,
    WordFormatOption,
    HTMLFormatOption,
    MarkdownFormatOption,
    AsciiDocFormatOption,
    CsvFormatOption,
)
from docling_core.types.doc import TableItem, TextItem

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractCliOcrOptions

logger = logging.getLogger(__name__)


class DoclingFileExtractor(InformationFileExtractor):
    """InformationFileExtractor implemented with Docling."""

    DEBUG = False

    def __init__(self, file_service: FileService):
        """Initialize the DoclingFileExtractor with the given FileService.

        Parameters
        ----------
        file_service : FileService
            The file service to use for file operations.
        """
        super().__init__(file_service)
        ocr = TesseractCliOcrOptions(lang=["deu", "eng"])
        pipe_options = PdfPipelineOptions(
            ocr_options=ocr,
            do_table_structure=True,
            generate_page_images=self.DEBUG,
            images_scale=2.0,
        )

        format_options = {
            InputFormat.PDF: PdfFormatOption(ocr=True, pipeline_options=pipe_options),
            InputFormat.IMAGE: ImageFormatOption(ocr=True, pipeline_options=pipe_options),
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.XLSX: ExcelFormatOption(),
            InputFormat.HTML: HTMLFormatOption(),
            InputFormat.MD: MarkdownFormatOption(),
            InputFormat.ASCIIDOC: AsciiDocFormatOption(),
            InputFormat.CSV: CsvFormatOption(),
        }

        self._converter = DocumentConverter(format_options=format_options)

    @property
    def compatible_file_types(self) -> list[FileType]:
        """Return supported file types.

        Returns
        -------
        list[FileType]
            The list of supported file types.
        """
        return [
            FileType.PDF,
            FileType.DOCX,
            FileType.PPTX,
            FileType.XLSX,
            FileType.HTML,
            FileType.MD,
            FileType.ASCIIDOC,
            FileType.CSV,
            FileType.IMAGE,
        ]

    @staticmethod
    def _has_meaningful_table_content(table_markdown: str) -> bool:
        return bool(re.search(r"\w", table_markdown))  # Check for at least one alphanumeric character

    @staticmethod
    def _resolve_item_page(item: Any) -> int:
        provenance = getattr(item, "prov", None)
        if isinstance(provenance, list):
            for prov_entry in provenance:
                page = getattr(prov_entry, "page_no", None)
                if isinstance(page, int):
                    return page
        return -1  # Default page number when not found

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """Extract content from the given file path.

        Parameters
        ----------
        file_path : Path
            Path to the file to extract content from.
        name : str
            Name of the document.

        Returns
        -------
        list[InternalInformationPiece]
            Extracted information pieces.
        """
        conversion_result: ConversionResult | None = None
        conversion_result = self._converter.convert(file_path)
        document = conversion_result.document

        if self.DEBUG:
            self._store_reading_order_images(document, Path("/app/services/document-extractor/log"))

        text_segments, table_segments = self._collect_page_segments(document)

        pieces: list[InternalInformationPiece] = self._create_information_pieces(
            text_segments,
            name,
            ContentType.TEXT,
        )
        table_pieces = [
            self._create_information_piece(
                document_name=name,
                page=page,
                content=table_markdown,
                content_type=ContentType.TABLE,
                additional_meta={
                    "origin_extractor": "docling",
                    "format": "markdown",
                    "table_index": index,
                },
            )
            for page, tables in table_segments.items()
            for index, table_markdown in enumerate(tables, start=1)
        ]

        return pieces + table_pieces

    def _store_reading_order_images(self, document, base_path: Path):
        viz = document.get_visualization(
            viz_mode="reading_order",
            show_branch_numbering=True,
        )

        for page_no, image in viz.items():
            image.save(base_path / f"reading_order_page_{page_no}.png")

    def _create_information_pieces(self, segments, name, content_type: ContentType) -> list[InternalInformationPiece]:
        pieces: list[InternalInformationPiece] = []

        for page_number in sorted(segments):  # when ordered dict, sort not needed
            segs = [segment for segment in segments[page_number] if segment]
            if not segs:
                continue
            markdown_content = "\n\n".join(segs)
            if not markdown_content.strip():
                continue
            pieces.append(
                self._create_information_piece(
                    document_name=name,
                    page=page_number,
                    content=markdown_content,
                    content_type=content_type,
                    additional_meta={
                        "origin_extractor": "docling",
                        "format": "markdown",
                    },
                )
            )

        return pieces

    def _collect_page_segments(self, document: Any) -> tuple[dict[int, list], dict[int, list]]:
        iterator = getattr(document, "iterate_items", None)
        if not callable(iterator):
            return {}, {}

        segments: dict[int, list[str]] = defaultdict(list)
        table_segments: dict[int, list[str]] = defaultdict(list)
        for item, _level in iterator():
            if isinstance(item, TextItem):
                text = getattr(item, "text", "")
                if not text:
                    continue
                page_number = self._resolve_item_page(item)
                segments[page_number].append(text)
            elif isinstance(item, TableItem):
                table_markdown = item.export_to_markdown()
                if not table_markdown:
                    continue
                if not self._has_meaningful_table_content(table_markdown):
                    continue
                page_number = self._resolve_item_page(item)
                table_segments[page_number].append(table_markdown)
        return segments, table_segments

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
