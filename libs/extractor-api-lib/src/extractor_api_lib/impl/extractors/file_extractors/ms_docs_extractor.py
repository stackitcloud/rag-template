"""Module containing the MSDocsExtractor class."""

import logging
from io import StringIO
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from unstructured.documents.elements import Element
from unstructured.partition.docx import partition_docx
from unstructured.partition.pptx import partition_pptx


from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.table_converter.dataframe_converter import DataframeConverter

logger = logging.getLogger(__name__)


class MSDocsExtractor(InformationFileExtractor):
    """Extractor for Microsoft Documents (DOCX and PPTX) using unstructured library."""

    def __init__(self, file_service: FileService, dataframe_converter: DataframeConverter):
        """
        Initialize the MSDocsExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        dataframe_converter : DataframeConverter
            Converter for dataframes to desired format.
        """
        super().__init__(file_service=file_service)
        self._dataframe_converter = dataframe_converter

    @property
    def compatible_file_types(self) -> list[FileType]:
        """
        List of compatible file types for the document parser.

        Returns
        -------
        list[FileType]
            A list containing the compatible file types, specifically DOCX and PPTX.
        """
        return [FileType.DOCX, FileType.PPTX]

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """
        Extract content from a given file based on its extension.

        Parameters
        ----------
        file_path : Path
            The path to the file from which content is to be extracted.
        name : str
            Name of the document.
        Returns
        -------
        list[InformationPiece]
            A list of InformationPiece objects extracted from the file.

        Raises
        ------
        ValueError
            If the file type is unsupported.

        Notes
        -----
        Supported file types are:
        - .docx
        - .pptx
        """
        extension = file_path.suffix.lower()
        match extension:
            case ".docx":
                partition_func = partition_docx
            case ".pptx":
                partition_func = partition_pptx
            case _:
                raise ValueError(f"Unsupported file type: {extension}")

        elements = partition_func(
            filename=file_path.as_posix(),
            include_page_breaks=True,
            infer_table_structure=True,
        )

        return self._process_elements(elements, name)

    def _process_elements(self, elements: list[Element], document_name: str) -> list[InternalInformationPiece]:
        processed_elements: list[InternalInformationPiece] = []
        page_content_lines: list[tuple[str, str]] = []
        current_page: int = 1
        old_page: int = 1

        for el in elements:
            current_page = el.metadata.page_number or current_page
            if old_page != current_page:
                if page_content_lines:
                    processed_elements.append(self._create_text_piece(document_name, old_page, page_content_lines))
                    page_content_lines = []
                old_page = current_page

            if el.text.strip():
                self._process_element(el, page_content_lines, processed_elements, document_name, current_page)

        if page_content_lines:
            processed_elements.append(self._create_text_piece(document_name, current_page, page_content_lines))

        return processed_elements

    def _process_element(
        self,
        el: Element,
        page_content_lines: list[tuple[str, str]],
        processed_elements: list[InternalInformationPiece],
        document_name: str,
        current_page: int,
    ) -> None:
        match el.category:
            case "Header":
                return

            case "Title":
                markdown_title = f"{'#' * el.metadata.category_depth} {el.text}"
                page_content_lines.append((el.category, markdown_title))

            case "Table":
                table_content = self._process_table(el, page_content_lines)
                processed_elements.append(
                    self._create_information_piece(
                        document_name,
                        current_page,
                        table_content,
                        ContentType.TABLE,
                    )
                )

            case _:
                page_content_lines.append((el.category, el.text))

    def _process_table(self, el: Element, page_content_lines: list[tuple[str, str]]) -> str:
        table_prev_content = ""
        if page_content_lines:
            _, last_element = page_content_lines[-1]
            table_prev_content += last_element + "\n"
        table = self._dataframe_converter.convert(pd.read_html(StringIO(el.metadata.text_as_html))[0])
        return table_prev_content + table

    def _create_text_piece(
        self, document_name: str, page: int, page_content_lines: list[tuple[str, str]]
    ) -> InternalInformationPiece:
        content = "\n".join([content for _, content in page_content_lines])
        return self._create_information_piece(document_name, page, content, ContentType.TEXT)

    def _create_information_piece(
        self,
        document_name: str,
        page: int,
        content: str,
        content_type: ContentType,
        additional_meta: Optional[dict[str, Any]] = None,
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
