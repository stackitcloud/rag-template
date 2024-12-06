"""Module containing the XMLExtractor class."""

import logging
from pathlib import Path
from typing import Optional, Any
import re

from extractor_api_lib.models.dataclasses.information_piece import InformationPiece
from unstructured.partition.xml import partition_xml
from unstructured.documents.elements import Element

from extractor_api_lib.document_parser.information_extractor import InformationExtractor
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.utils.utils import hash_datetime

logger = logging.getLogger(__name__)


class XMLExtractor(InformationExtractor):
    """Extractor for XML documents using unstructured library."""

    def __init__(self, file_service: FileService):
        """Initialize the XMLExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        """
        super().__init__(file_service=file_service)

    @property
    def compatible_file_types(self) -> list[FileType]:
        """
        List of compatible file types for the XML extractor.

        Returns
        -------
        list[FileType]
            A list containing the compatible file types, which in this case is XML.
        """
        return [FileType.XML]

    def extract_content(self, file_path: Path) -> list[InformationPiece]:
        """
        Extract content from an XML file and processes the elements.

        Parameters
        ----------
        file_path : Path
            The path to the XML file to be processed.

        Returns
        -------
        list[InformationPiece]
            A list of processed information pieces extracted from the XML file.
        """
        elements = partition_xml(filename=file_path.as_posix(), xml_keep_tags=False)
        return self._process_elements(elements, file_path.name)

    def _process_elements(self, elements: list[Element], document_name: str) -> list[InformationPiece]:
        processed_elements: list[InformationPiece] = []
        content_lines: list[tuple[str, str]] = []

        for el in elements:
            if el.text.strip():
                self._process_element(el, content_lines)

        if content_lines:
            processed_elements.append(self._create_text_piece(document_name, content_lines))

        return processed_elements

    def _process_element(self, el: Element, content_lines: list[tuple[str, str]]) -> None:
        sanitized_text = self._sanitize_text(el.text)

        if el.category == "Title":
            markdown_title = f"# {sanitized_text}"
            content_lines.append((el.category, markdown_title))
        else:
            content_lines.append((el.category, sanitized_text))

    def _sanitize_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _create_text_piece(self, document_name: str, content_lines: list[tuple[str, str]]) -> InformationPiece:
        content = "\n".join([content for _, content in content_lines])
        return self._create_information_piece(document_name, content, ContentType.TEXT)

    def _create_information_piece(
        self,
        document_name: str,
        content: str,
        content_type: ContentType,
        additional_meta: Optional[dict[str, Any]] = None,
    ) -> InformationPiece:
        metadata = {
            "document": document_name,
            "id": hash_datetime(),
            "related": [],
        }
        if additional_meta:
            metadata.update(additional_meta)
        return InformationPiece(
            type=content_type,
            metadata=metadata,
            page_content=content,
        )
