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


from extractor_api_lib.impl.settings.pdf_extractor_settings import PDFExtractorSettings
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.impl.utils.utils import hash_datetime
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.table_converter.dataframe_converter import DataframeConverter
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor

logger = logging.getLogger(__name__)


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
    """

    TITLE_PATTERN = re.compile(r"(^|\n)(\d+\.[\.\d]*[\t ][a-zA-Z0-9 äöüÄÖÜß\-]+)")
    TITLE_PATTERN_MULTILINE = re.compile(r"(^|\n)(\d+\.[\.\d]*[\t ][a-zA-Z0-9 äöüÄÖÜß\-]+)", re.MULTILINE)

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
    ) -> InternalInformationPiece:
        metadata = {
            "document": document_name,
            "page": page,
            "title": title,
            "id": information_id,
            "related": [],
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
        # Step 1: Convert each PDF page to an image
        images = convert_from_path(file_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, image in enumerate(images, 1):
                image.save(Path(temp_dir, f"page_{i}.png").as_posix(), "PNG")

            # Step 2: Use pdfplumber to identify table/figure coordinates and extract text
            pdf_elements = []

            current_title = ""
            with pdfplumber.open(file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages, 1):
                    logger.debug("Processing page: %d" % page_idx)
                    (new_pdf_elements, current_title) = self._extract_content_from_page(
                        page_index=page_idx,
                        page=page,
                        temp_dir=temp_dir,
                        title=current_title,
                        document_name=name,
                    )
                    pdf_elements += new_pdf_elements

        return pdf_elements

    def _extract_tabluar_data(
        self,
        page: Page,
        page_index: int,
        document_name: str,
        text_x_tolerance: int = 1,
        text_y_tolerance: int = 1,
    ) -> list[InternalInformationPiece]:
        return_value = []
        pdfplumber_tables = page.find_tables()
        table_strings = []
        for table in pdfplumber_tables:
            table_df = pd.DataFrame(table.extract(x_tolerance=text_x_tolerance, y_tolerance=text_y_tolerance))
            try:
                converted_table = self._dataframe_converter.convert(table_df)
            except TypeError as e:
                logger.error(f"Error while converting table to string: {e}")
                continue
            if converted_table == "":
                continue
            table_strings.append(self._dataframe_converter.convert(table_df))

        if table_strings:
            for table_content in table_strings:
                return_value.append(
                    self._create_information_piece(
                        document_name,
                        page_index,
                        "",
                        table_content,
                        ContentType.TABLE,
                        information_id=hash_datetime(),
                    )
                )

        return return_value

    def _extract_text(
        self,
        page: Page,
        scale_x: int,
        scale_y: int,
        image: np.ndarray,
        pdf_page_height: int,
        pdf_page_width: int,
    ) -> str:
        thickness = -1
        color = (255, 255, 255)
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

        imgs = page.images
        for img in imgs:
            start_point = (
                int(img["x0"] * scale_x),
                int((pdf_page_height - img["y1"]) * scale_y),
            )
            end_point = (
                int(img["x1"] * scale_x),
                int((pdf_page_height - img["y0"]) * scale_y),
            )
            cv2.rectangle(image, start_point, end_point, color, thickness)
        lx = 0
        ly = 0
        start_point = (lx, ly)
        ux = int(pdf_page_width * scale_x)
        uy = 150
        end_point = (ux, uy)

        cv2.rectangle(image, start_point, end_point, color, thickness)

        ly = int(pdf_page_height * scale_y - 160)
        start_point = (lx, ly)
        ux = int(pdf_page_width * scale_x)
        uy = int(pdf_page_height * scale_y)
        end_point = (ux, uy)

        cv2.rectangle(image, start_point, end_point, color, thickness)

        return pytesseract.image_to_string(image, lang="deu")

    def _extract_content_from_page(
        self,
        page_index: int,
        page: Page,
        temp_dir: str,
        title: str,
        document_name: str,
    ):
        pdf_elements = []

        im_path = Path(temp_dir, f"page_{page_index}.png")
        image = cv2.imread(im_path.as_posix())
        pdf_page_width = page.width
        pdf_page_height = page.height
        image_page_width = image.shape[1]
        image_page_height = image.shape[0]
        scale_x = image_page_width / pdf_page_width
        scale_y = image_page_height / pdf_page_height

        content = self._extract_text(
            page=page,
            scale_x=scale_x,
            scale_y=scale_y,
            image=image,
            pdf_page_height=pdf_page_height,
            pdf_page_width=pdf_page_width,
        )

        if not content:
            return [], title

        content_array = re.split(self.TITLE_PATTERN_MULTILINE, content)
        content_array = [x.strip() for x in content_array if x and x.strip()]

        for content_item in content_array:
            is_title = re.match(self.TITLE_PATTERN, content_item)
            if is_title:
                title = content_item
            else:
                pdf_elements.append(
                    self._create_information_piece(
                        document_name,
                        page_index,
                        title,
                        title + "\n" + content_item,
                        ContentType.TEXT,
                        information_id=hash_datetime(),
                    )
                )
        table_elements = self._extract_tabluar_data(
            page=page,
            page_index=page_index,
            document_name=document_name,
        )

        if table_elements:
            pdf_elements += table_elements

        return pdf_elements, title
