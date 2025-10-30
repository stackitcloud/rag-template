"""Module containing the PDFExtractor class."""

import logging
import re
import tempfile
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pdfplumber.page import Page
from langdetect import detect
import camelot


from extractor_api_lib.impl.settings.pdf_extractor_settings import PDFExtractorSettings
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.table_converter.dataframe_converter import DataframeConverter
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor

logger = logging.getLogger(__name__)
logging.getLogger("pdfminer").setLevel(logging.WARNING)


class PDFExtractor(InformationFileExtractor):
    """PDFExtractor is a class responsible for extracting information from PDF files.

    It converts PDF pages to images, identifies table/figure coordinates, and extracts
    text content using OCR.

    Attributes
    ----------
    TITLE_PATTERN : re.Pattern
        Regular expression pattern to identify titles in the text.document
    TITLE_PATTERN_MULTILINE : re.Pattern
        Regular expression pattern to identify titles in the text with multiline support.
    TEXT_THRESHOLD : float
        Threshold for determining if a page has extractable text (default: 50 characters).
    """

    TITLE_PATTERN = re.compile(r"(^|\n)(\d+\.[\.\d]*[\t ][a-zA-Z0-9 äöüÄÖÜß\-]+)")
    TITLE_PATTERN_MULTILINE = re.compile(r"(^|\n)(\d+\.[\.\d]*[\t ][a-zA-Z0-9 äöüÄÖÜß\-]+)", re.MULTILINE)
    TEXT_THRESHOLD = 50  # Minimum characters to consider page as text-based

    def __init__(
        self,
        file_service: FileService,
        pdf_extractor_settings: PDFExtractorSettings,
        dataframe_converter: DataframeConverter,
    ):
        """Initialize the PDFExtractor.

        Parameters
        ----------
        file_service : FileService
            Handler for downloading the file to extract content from and upload results to if required.
        pdf_extractor_settings : PDFExtractorSettings
            Settings for the pdf extractor.
        dataframe_converter: DataframeConverter
            Converter for dataframe tables to a search and saveable format.
        """
        super().__init__(file_service=file_service)
        self._dataframe_converter = dataframe_converter
        self._settings = pdf_extractor_settings
        self.old_image_id = None
        self._lang_map = {
            "en": "eng",
            "de": "deu",
        }

    @property
    def compatible_file_types(self) -> list[FileType]:
        """
        Returns a list of compatible file types for the PDF extractor.

        Returns
        -------
        list[FileType]
            A list containing the FileType.PDF indicating that this extractor is compatible with PDF files.
        """
        return [FileType.PDF]

    @staticmethod
    def _create_information_piece(
        document_name: str,
        page: int,
        title: str,
        content: str,
        content_type: ContentType,
        information_id: str,
        additional_meta: Optional[dict] = None,
        related_ids: list[str] = None,
    ) -> InternalInformationPiece:
        metadata = {
            "document": document_name,
            "page": page,
            "title": title,
            "id": information_id,
            "related": related_ids if related_ids else [],
        }
        if additional_meta:
            metadata = metadata | additional_meta
        return InternalInformationPiece(
            type=content_type,
            metadata=metadata,
            page_content=content,
        )

    async def aextract_content(self, file_path: Path, name: str) -> list[InternalInformationPiece]:
        """Extract content from given file.

        Parameters
        ----------
        file_path : Path
            Path to the file the information should be extracted from.
        name : str
            Name of the document.

        Returns
        -------
        list[InformationPiece]
            The extracted information.
        """
        images = convert_from_path(file_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, image in enumerate(images, 1):
                image.save(Path(temp_dir, f"page_{i}.png").as_posix(), "PNG")

            pdf_elements = []

            current_title = ""
            with pdfplumber.open(file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages, 1):
                    logger.debug("Processing page: %d/%d", page_idx, len(pdf.pages))

                    is_text_based = self._is_text_based(page)

                    (new_pdf_elements, current_title) = self._extract_content_from_page(
                        page_index=page_idx,
                        page=page,
                        is_text_based=is_text_based,
                        temp_dir=temp_dir,
                        title=current_title,
                        document_name=name,
                    )
                    pdf_elements += new_pdf_elements

            logger.info("Extraction completed. Found %d information pieces.", len(pdf_elements))
            return pdf_elements

    def _is_text_based(self, page: Page) -> bool:
        """Classify whether a page is text-based, scanned.

        Parameters
        ----------
        page : Page
            The pdfplumber page object.

        Returns
        -------
        bool
            returns True if the page is text-based, False if it is scanned.
        """
        # Try to extract text using pdfplumber
        extractable_text = page.extract_text() or ""

        # Clean and count meaningful text
        meaningful_text = re.sub(r"\s+", " ", extractable_text.strip())

        if len(meaningful_text) >= self.TEXT_THRESHOLD:
            return True
        return False

    def _extract_tables_from_text_page(
        self,
        page: Page,
        page_index: int,
        document_name: str,
        text_x_tolerance: int = 1,
        text_y_tolerance: int = 1,
    ) -> list[InternalInformationPiece]:
        table_elements = []

        try:
            pdfplumber_tables = page.find_tables()

            for idx, table in enumerate(pdfplumber_tables):
                table_data = table.extract(x_tolerance=text_x_tolerance, y_tolerance=text_y_tolerance)
                if not table_data or all(not row or all(not cell for cell in row) for row in table_data):
                    continue
                table_df = pd.DataFrame(table_data)
                try:
                    converted_table = self._dataframe_converter.convert(table_df)
                except TypeError:
                    logger.exception("Error while converting table to string")
                    continue
                if not converted_table.strip():
                    continue
                table_elements.append(
                    self._create_information_piece(
                        document_name,
                        page_index,
                        f"Table {idx + 1}",
                        converted_table,
                        ContentType.TABLE,
                        information_id=hash_datetime(),
                    )
                )
        except Exception:
            logger.warning("Failed to find tables on page %d", page_index, exc_info=True)

        return table_elements

    def _auto_detect_language(self, text):
        try:
            return detect(text)
        except Exception:
            return "en"

    def _extract_text_from_scanned_page(
        self,
        page: Page,
        scale_x: int,
        scale_y: int,
        image: np.ndarray,
        pdf_page_height: int,
        with_image_masking: Optional[bool] = True,
    ) -> tuple[str, bytes]:
        thickness = -1
        color = (255, 255, 255)
        original_image = image.copy()
        for table in page.find_tables():
            table_coords = table.bbox
            start_point = (
                int(table_coords[0] * scale_x),
                int(table_coords[1] * scale_y),
            )
            end_point = (
                int(table_coords[2] * scale_x),
                int(table_coords[3] * scale_y),
            )

            cv2.rectangle(image, start_point, end_point, color, thickness)

        if with_image_masking:
            for img in page.images:
                start_point = (
                    int(img["x0"] * scale_x),
                    int((pdf_page_height - img["y1"]) * scale_y),
                )
                end_point = (
                    int(img["x1"] * scale_x),
                    int((pdf_page_height - img["y0"]) * scale_y),
                )
                cv2.rectangle(image, start_point, end_point, color, thickness)

        rough_text = pytesseract.image_to_string(image, lang="eng")
        if not rough_text and with_image_masking:
            return self._extract_text_from_scanned_page(
                page, scale_x, scale_y, original_image, pdf_page_height, with_image_masking=False
            )
        lang_code = self._auto_detect_language(rough_text)
        tesseract_lang = self._lang_map.get(lang_code, "eng")
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(original_image, extension="pdf", lang=tesseract_lang)
        if lang_code == "en":
            return (rough_text, pdf_bytes)

        return (pytesseract.image_to_string(image, lang=tesseract_lang), pdf_bytes)

    def _extract_tables_from_scanned_page(
        self, page_index: int, document_name: str, filename: str
    ) -> list[InternalInformationPiece]:
        """Extract tables from scanned page using multiple methods.

        Parameters
        ----------
        page_index : int
            The page number.
        document_name : str
            Name of the document.
        filename: str
            Path to the PDF file including the filename.

        Returns
        -------
        list[InternalInformationPiece]
            List of extracted table information pieces.
        """
        table_elements = []

        # Method 1: Try Camelot (good for scanned tables)
        try:
            camelot_tables = camelot.read_pdf(str(filename))

            for i, table in enumerate(camelot_tables):
                if table.accuracy > 50:  # Only use tables with good accuracy
                    try:
                        converted_table = self._dataframe_converter.convert(table.df)
                        if converted_table and converted_table.strip():
                            table_elements.append(
                                self._create_information_piece(
                                    document_name,
                                    page_index,
                                    f"Table {i + 1}",
                                    converted_table,
                                    ContentType.TABLE,
                                    information_id=hash_datetime(),
                                    additional_meta={
                                        "table_method": "camelot",
                                        "accuracy": table.accuracy,
                                        "table_index": i,
                                    },
                                )
                            )
                    except Exception:
                        logger.warning("Failed to convert Camelot table %d", i + 1, exc_info=True)

        except Exception:
            logger.debug("Camelot table extraction failed for page %d", page_index, exc_info=True)

        return table_elements

    def _extract_text_from_text_page(self, page: Page) -> str:
        try:
            return page.extract_text() or ""
        except Exception:
            logger.warning("Failed to extract text with pdfplumber", exc_info=True)
            return ""

    def _extract_content_from_page(
        self,
        page_index: int,
        page: Page,
        is_text_based: bool,
        temp_dir: str,
        title: str,
        document_name: str,
    ) -> tuple[list[InternalInformationPiece], str]:

        im_path = Path(temp_dir, f"page_{page_index}.png")
        image = cv2.imread(im_path.as_posix())
        pdf_page_width = page.width
        pdf_page_height = page.height
        image_page_width = image.shape[1]
        image_page_height = image.shape[0]
        scale_x = image_page_width / pdf_page_width
        scale_y = image_page_height / pdf_page_height
        content = ""
        table_elements = []
        if is_text_based:
            content = self._extract_text_from_text_page(page)
            table_elements = self._extract_tables_from_text_page(
                page=page, page_index=page_index, document_name=document_name
            )
        else:
            content, pdf_bytes = self._extract_text_from_scanned_page(
                page=page,
                scale_x=scale_x,
                scale_y=scale_y,
                image=image,
                pdf_page_height=pdf_page_height,
            )

            abs_filename = Path(temp_dir, f"page_{page_index}.pdf").as_posix()
            with open(abs_filename, "wb") as f:
                f.write(pdf_bytes)
            table_elements = self._extract_tables_from_scanned_page(
                page_index=page_index,
                document_name=document_name,
                filename=abs_filename,
            )

        text_element_ids = []
        pdf_elements = []
        if content and content.strip():
            pdf_elements = self._process_text_content(content, title, page_index, document_name)
            for element in pdf_elements:
                text_element_ids.append(element.metadata["id"])

        if table_elements:
            tmp_table_elements = []
            table_element_ids = []
            for element in table_elements:
                element.metadata["related"] = text_element_ids
                tmp_table_elements.append(element)
                table_element_ids.append(element.metadata["id"])
            tmp_pdf_elements = []
            for element in pdf_elements:
                element.metadata["related"] = table_element_ids
                tmp_pdf_elements.append(element)

            pdf_elements = tmp_pdf_elements + tmp_table_elements

        return pdf_elements, title

    def _process_text_content(
        self, content: str, title: str, page_index: int, document_name: str
    ) -> list[InternalInformationPiece]:
        """Process text content and split by titles.

        Parameters
        ----------
        content : str
            Raw text content.
        title : str
            Current title context.
        page_index : int
            The page number.
        document_name : str
            Name of the document.

        Returns
        -------
        list[InternalInformationPiece]
            List of processed text information pieces.
        """
        text_elements = []

        if not content or not content.strip():
            return text_elements

        # Split content by title patterns
        content_array = re.split(self.TITLE_PATTERN_MULTILINE, content)
        content_array = [x.strip() for x in content_array if x and x.strip()]

        current_title = title

        for content_item in content_array:
            is_title = re.match(self.TITLE_PATTERN, content_item)
            if is_title:
                current_title = content_item.strip()
            else:
                # Create text piece with current title context
                full_content = f"{current_title}\n{content_item}" if current_title else content_item

                text_elements.append(
                    self._create_information_piece(
                        document_name,
                        page_index,
                        current_title,
                        full_content,
                        ContentType.TEXT,
                        information_id=hash_datetime(),
                    )
                )

        return text_elements
