"""Comprehensive test suite for PDFExtractor class."""

import time
import logging

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import pandas as pd
import numpy as np
from pdf2image.exceptions import PDFPageCountError
import pdfplumber
from pdf2image import convert_from_path

from extractor_api_lib.impl.extractors.file_extractors.pdf_extractor import PDFExtractor
from extractor_api_lib.impl.settings.pdf_extractor_settings import PDFExtractorSettings
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.table_converter.dataframe_converter import DataframeConverter

logger = logging.getLogger(__name__)


class TestPDFExtractor:
    """Test class for PDFExtractor."""

    @pytest.fixture
    def mock_pdf_extractor_settings(self):
        """Create mock PDF extractor settings."""
        return MagicMock(spec=PDFExtractorSettings)

    @pytest.fixture
    def mock_dataframe_converter(self):
        """Create a mock dataframe converter."""
        converter = MagicMock(spec=DataframeConverter)
        converter.convert.return_value = "Mocked table content"
        return converter

    @pytest.fixture
    def pdf_extractor(self, mock_file_service, mock_pdf_extractor_settings, mock_dataframe_converter):
        """Create a PDFExtractor instance for testing."""
        return PDFExtractor(
            file_service=mock_file_service,
            pdf_extractor_settings=mock_pdf_extractor_settings,
            dataframe_converter=mock_dataframe_converter,
        )

    @pytest.fixture
    def test_pdf_files(self):
        """Provide paths to test PDF files."""
        test_data_dir = Path(__file__).parent / "test_data"
        return {
            "text_based": test_data_dir / "text_based_document.pdf",
            "scanned": test_data_dir / "scanned_document.pdf",
            "mixed_content": test_data_dir / "mixed_content_document.pdf",
            "multi_column": test_data_dir / "multi_column_document.pdf",
        }

    def test_compatible_file_types(self, pdf_extractor):
        """Test that PDF extractor only supports PDF files."""
        compatible_types = pdf_extractor.compatible_file_types
        assert compatible_types == [FileType.PDF]

    def test_create_information_piece(self):
        """Test the static method for creating information pieces."""
        piece = PDFExtractor._create_information_piece(
            document_name="test_doc",
            page=1,
            title="Test Title",
            content="Test content",
            content_type=ContentType.TEXT,
            information_id="test_id",
            additional_meta={"test_key": "test_value"},
            related_ids=["related_1", "related_2"],
        )

        assert isinstance(piece, InternalInformationPiece)
        assert piece.type == ContentType.TEXT
        assert piece.page_content == "Test content"
        assert piece.metadata["document"] == "test_doc"
        assert piece.metadata["page"] == 1
        assert piece.metadata["title"] == "Test Title"
        assert piece.metadata["id"] == "test_id"
        assert piece.metadata["related"] == ["related_1", "related_2"]
        assert piece.metadata["test_key"] == "test_value"

    def test_is_text_based_threshold(self, pdf_extractor):
        """Test the text-based page classification threshold."""
        # Mock pdfplumber page
        mock_page = MagicMock()

        # Test case 1: Page with enough text (above threshold)
        mock_page.extract_text.return_value = "A" * 60  # Above 50 character threshold
        assert pdf_extractor._is_text_based(mock_page) is True

        # Test case 2: Page with insufficient text (below threshold)
        mock_page.extract_text.return_value = "A" * 30  # Below 50 character threshold
        assert pdf_extractor._is_text_based(mock_page) is False

        # Test case 3: Empty text
        mock_page.extract_text.return_value = ""
        assert pdf_extractor._is_text_based(mock_page) is False

        # Test case 4: None text
        mock_page.extract_text.return_value = None
        assert pdf_extractor._is_text_based(mock_page) is False

    def test_auto_detect_language(self, pdf_extractor):
        """Test language detection functionality."""
        # Test English text
        english_text = "This is a sample English text for language detection."
        detected_lang = pdf_extractor._auto_detect_language(english_text)
        assert detected_lang == "en"  # Should detect a language
        # Test German text
        german_text = "Dies ist ein deutscher Beispiel Text für die Spracherkennung"
        detected_lang = pdf_extractor._auto_detect_language(german_text)
        assert detected_lang == "de"

        # Test with empty text (should default to "en")
        empty_text = ""
        detected_lang = pdf_extractor._auto_detect_language(empty_text)
        assert detected_lang == "en"

    @pytest.mark.asyncio
    async def test_extract_content_text_based_pdf(self, pdf_extractor, test_pdf_files):
        """Test content extraction from text-based PDF."""
        result = await pdf_extractor.aextract_content(
            file_path=test_pdf_files["text_based"], name="text_based_document"
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Check that we have both text and table elements
        text_elements = [elem for elem in result if elem.type == ContentType.TEXT]
        table_elements = [elem for elem in result if elem.type == ContentType.TABLE]

        assert len(text_elements) > 0, "Should extract at least one text element"
        assert len(table_elements) > 0, "Should extract at least one table element"

        # Verify metadata structure
        for element in result:
            assert "document" in element.metadata
            assert "page" in element.metadata
            assert "title" in element.metadata
            assert "id" in element.metadata
            assert "related" in element.metadata
            assert element.metadata["document"] == "text_based_document"

    @pytest.mark.asyncio
    async def test_extract_content_scanned_pdf(self, pdf_extractor, test_pdf_files):
        """Test content extraction from scanned PDF using OCR."""
        result = await pdf_extractor.aextract_content(file_path=test_pdf_files["scanned"], name="scanned_document")

        assert isinstance(result, list)

        for element in result:
            assert element.metadata["document"] == "scanned_document"
            assert isinstance(element.metadata["page"], int)

    @pytest.mark.asyncio
    async def test_extract_content_mixed_content_pdf(self, pdf_extractor, test_pdf_files):
        """Test content extraction from mixed content PDF."""
        result = await pdf_extractor.aextract_content(
            file_path=test_pdf_files["mixed_content"], name="mixed_content_document"
        )

        assert isinstance(result, list)
        assert len(result) > 0

        content_types = {elem.type for elem in result}
        assert ContentType.TEXT in content_types
        assert ContentType.TABLE in content_types

        for element in result:
            assert element.metadata["document"] == "mixed_content_document"

    @pytest.mark.asyncio
    async def test_extract_content_multi_column_pdf(self, pdf_extractor, test_pdf_files):
        """Test content extraction from multi-column PDF."""
        result = await pdf_extractor.aextract_content(
            file_path=test_pdf_files["multi_column"], name="multi_column_document"
        )

        assert isinstance(result, list)
        assert len(result) > 0

        for element in result:
            assert element.metadata["document"] == "multi_column_document"

    def test_process_text_content_with_titles(self, pdf_extractor):
        """Test text content processing with title detection."""
        content = """1. Introduction
This is the introduction section with substantial content.
It contains multiple sentences and paragraphs.

2. Methodology
This section describes the methodology used in the research.
It includes detailed explanations of procedures.

3. State of the art
This section describes the state of the art.

3.1 Data Collection
This subsection covers data collection procedures.
"""

        result = pdf_extractor._process_text_content(
            content=content, title="Document Title", page_index=1, document_name="test_document"
        )

        assert isinstance(result, list)
        assert len(result) == 4

        # Check that titles are properly detected and content is split
        content_found = [elem.page_content for elem in result]

        # Should contain the processed content
        assert any("1. Introduction" in content for content in content_found)
        assert any("2. Methodology" in content for content in content_found)

        for elem in result:
            assert elem.metadata["title"] in [
                "1. Introduction",
                "2. Methodology",
                "3. State of the art",
                "3.1 Data Collection",
            ]

    def test_process_text_content_without_titles(self, pdf_extractor):
        """Test text content processing without title patterns."""
        content = "This is plain text content without any title patterns."

        result = pdf_extractor._process_text_content(
            content=content, title="Current Title", page_index=1, document_name="test_document"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].metadata["title"] == "Current Title"
        assert "Current Title" in result[0].page_content

    def test_process_empty_text_content(self, pdf_extractor):
        """Test processing empty or None text content."""
        # Test empty string
        result = pdf_extractor._process_text_content(
            content="", title="Title", page_index=1, document_name="test_document"
        )
        assert result == []

        # Test whitespace only
        result = pdf_extractor._process_text_content(
            content="   \n\t   ", title="Title", page_index=1, document_name="test_document"
        )
        assert result == []

    # TODO: hier gehts weiter !!! D:

    def test_extract_text_from_text_page(self, pdf_extractor):
        """Test text extraction from text-based pages."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample extracted text"

        result = pdf_extractor._extract_text_from_text_page(mock_page)
        assert result == "Sample extracted text"

        # Test error handling
        mock_page.extract_text.side_effect = Exception("Extraction failed")
        result = pdf_extractor._extract_text_from_text_page(mock_page)
        assert result == ""

    def test_extract_tables_from_text_page(self, pdf_extractor):
        """Test table extraction from text-based pages."""
        mock_page = MagicMock()

        # Mock table data
        mock_table = MagicMock()
        mock_table.extract.return_value = [["Header 1", "Header 2"], ["Value 1", "Value 2"], ["Value 3", "Value 4"]]
        mock_page.find_tables.return_value = [mock_table]

        result = pdf_extractor._extract_tables_from_text_page(
            page=mock_page, page_index=1, document_name="test_document"
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].type == ContentType.TABLE
        assert result[0].metadata["document"] == "test_document"
        assert result[0].metadata["page"] == 1

    @pytest.mark.integration
    def test_extract_text_from_scanned_page(self, pdf_extractor, test_pdf_files):
        """Test text extraction from scanned pages using OCR with real PDF."""

        # Use the actual scanned test PDF
        scanned_pdf_path = test_pdf_files["scanned"]

        # Open the real PDF and get the first page
        with pdfplumber.open(scanned_pdf_path) as pdf:

            page = pdf.pages[0]

            # Convert PDF page to image for OCR
            images = convert_from_path(scanned_pdf_path, first_page=1, last_page=1)

            # Convert PIL image to numpy array
            image_array = np.array(images[0])

            # Test the actual OCR extraction
            result = pdf_extractor._extract_text_from_scanned_page(
                page=page, scale_x=1.0, scale_y=1.0, image=image_array, pdf_page_height=images[0].height
            )

            assert isinstance(result, tuple)
            assert len(result) == 2
            text, pdf_bytes = result

            assert isinstance(text, str)
            assert isinstance(pdf_bytes, bytes)

            # The OCR should extract some text (even if not perfect)
            assert len(text.strip()) > 0, "OCR should extract some text from scanned page"

            # PDF bytes should be generated
            assert len(pdf_bytes) > 0, "Should generate PDF bytes from OCR"

            # Verify specific content from the scanned PDF
            expected_content = [
                "SCANNED DOCUMENT",
                "This document appears to be scanned from a physical paper",
                "text extraction capabilities are limited",
                "Key characteristics of scanned documents",
                "OCR is required for text extraction",
                "testing purposes",
            ]

            # Check that the main content elements are extracted
            text_upper = text.upper()
            for expected_phrase in expected_content:
                assert (
                    expected_phrase.upper() in text_upper
                ), f"Expected phrase '{expected_phrase}' not found in OCR text"

            with patch.object(pdf_extractor, "_auto_detect_language", return_value="de"):
                result = pdf_extractor._extract_text_from_scanned_page(
                    page=page, scale_x=1.0, scale_y=1.0, image=image_array, pdf_page_height=images[0].height
                )

                assert isinstance(result, tuple)
                assert len(result) == 2
                text, pdf_bytes = result
                assert isinstance(text, str)
                assert isinstance(pdf_bytes, bytes)

    @patch("camelot.read_pdf")
    def test_extract_tables_from_scanned_page(self, mock_camelot, pdf_extractor):
        """Test table extraction from scanned pages."""
        # Mock Camelot table extraction
        mock_camelot_table = MagicMock()
        mock_camelot_table.accuracy = 75
        mock_camelot_table.df = pd.DataFrame({"Column 1": ["Value 1", "Value 2"], "Column 2": ["Value 3", "Value 4"]})
        mock_camelot.return_value = [mock_camelot_table]

        result = pdf_extractor._extract_tables_from_scanned_page(
            page_index=1, document_name="test_document", filename="/path/to/test.pdf"
        )

        assert isinstance(result, list)
        if len(result) > 0:  # Camelot succeeded
            assert result[0].type == ContentType.TABLE
            assert result[0].metadata["table_method"] == "camelot"
            assert result[0].metadata["accuracy"] == 75

    def test_title_pattern_detection(self, pdf_extractor):
        """Test title pattern regular expressions with precise assertions."""
        # Test single line titles with TITLE_PATTERN.search()
        test_cases = [
            "1. Introduction",
            "2.1 Methodology",
            "3.1.1 Data Collection",
            "4.\tResults",
            "5. Discussion and Conclusions",
            "1.2.3.4.5 Many dots",
        ]

        for test_case in test_cases:
            match = pdf_extractor.TITLE_PATTERN.search(test_case)
            assert match is not None, f"TITLE_PATTERN should match: '{test_case}'"

            assert match.group(1) == "", f"Group 1 should be empty for start-of-string match, got: '{match.group(1)}'"

            extracted_title = match.group(2)
            assert extracted_title == test_case, f"Expected title '{test_case}', but extracted '{extracted_title}'"

        # Test titles that should NOT match (edge cases)
        non_matching_cases = [
            "Introduction without number",
            "A. Section with letter",
            "1.",  # No text after number
            "1 Missing dot",
        ]

        for non_match_case in non_matching_cases:
            match = pdf_extractor.TITLE_PATTERN.search(non_match_case)
            assert match is None, f"TITLE_PATTERN should NOT match: '{non_match_case}'"

        # Test multiline title detection with TITLE_PATTERN_MULTILINE.findall()
        multiline_text = """Some content here.

1. First Section
This is the content of the first section.

2. Second Section
This is the content of the second section.

3.1 Subsection Example
More content here."""

        matches = pdf_extractor.TITLE_PATTERN_MULTILINE.findall(multiline_text)
        expected_titles = ["1. First Section", "2. Second Section", "3.1 Subsection Example"]

        # Verify we found the expected number of matches
        assert len(matches) == 3, f"Should find 3 title patterns, found {len(matches)}: {matches}"

        # Each match is a tuple: (line_start_group, title_text_group)
        # Extract just the title text (group 2) from each match tuple
        found_titles = [match[1] for match in matches]

        # Compare the exact titles found vs expected
        assert found_titles == expected_titles, f"Expected titles {expected_titles}, but found {found_titles}"

        # Verify that group 1 contains newlines for multiline matches
        line_starts = [match[0] for match in matches]
        expected_line_starts = ["\n", "\n", "\n"]  # All should have newline since they're after content
        assert (
            line_starts == expected_line_starts
        ), f"Expected line starts {expected_line_starts}, but found {line_starts}"

        # Test edge case: title at very beginning of text
        text_with_title_at_start = "1. Starting Title\nSome content follows."
        start_matches = pdf_extractor.TITLE_PATTERN_MULTILINE.findall(text_with_title_at_start)
        assert len(start_matches) == 1, f"Should find 1 title at start, found: {start_matches}"
        assert start_matches[0][0] == "", f"Group 1 should be empty for start-of-text, got: '{start_matches[0][0]}'"
        assert start_matches[0][1] == "1. Starting Title", f"Should extract correct title, got: '{start_matches[0][1]}'"

    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self, pdf_extractor):
        """Test error handling with invalid PDF file."""
        invalid_path = Path("/nonexistent/file.pdf")

        with pytest.raises(PDFPageCountError):
            await pdf_extractor.aextract_content(file_path=invalid_path, name="invalid_document")

    @pytest.mark.asyncio
    async def test_related_ids_mapping(self, pdf_extractor, test_pdf_files):
        """Test that related IDs are properly set between text and table elements using actual extractor."""
        # Use the actual PDF extractor with a real test file
        for test_file in test_pdf_files.values():

            # Extract content using the actual extractor
            result = await pdf_extractor.aextract_content(file_path=test_file, name="test_document")

            # Filter text and table elements
            text_elements = [elem for elem in result if elem.type == ContentType.TEXT]
            table_elements = [elem for elem in result if elem.type == ContentType.TABLE]

            # Test only if we have both text and table elements from the same page
            if len(text_elements) > 0 and len(table_elements) > 0:
                # Check that text elements have table IDs in their related field
                text_element = text_elements[0]
                table_element = table_elements[0]

                # If elements are from the same page, they should reference each other
                same_page_text = [
                    elem for elem in text_elements if elem.metadata["page"] == table_element.metadata["page"]
                ]
                same_page_tables = [
                    elem for elem in table_elements if elem.metadata["page"] == text_element.metadata["page"]
                ]

                if same_page_text and same_page_tables:
                    # Get IDs from same page elements
                    same_page_text_ids = [elem.metadata["id"] for elem in same_page_text]
                    same_page_table_ids = [elem.metadata["id"] for elem in same_page_tables]

                    # Verify that table elements reference text elements from the same page
                    for table_elem in same_page_tables:
                        assert "related" in table_elem.metadata
                        related_ids = table_elem.metadata["related"]
                        # The related IDs should contain text element IDs from the same page
                        for text_id in same_page_text_ids:
                            assert text_id in related_ids, f"Table element should reference text element {text_id}"

                    # Verify that text elements reference table elements from the same page
                    for text_elem in same_page_text:
                        assert "related" in text_elem.metadata
                        related_ids = text_elem.metadata["related"]
                        # The related IDs should contain table element IDs from the same page
                        for table_id in same_page_table_ids:
                            assert table_id in related_ids, f"Text element should reference table element {table_id}"

            # Verify all elements have the related field (even if empty)
            for element in result:
                assert "related" in element.metadata, "All elements should have 'related' field in metadata"
                assert isinstance(element.metadata["related"], list), "'related' field should be a list"

    @pytest.mark.asyncio
    async def test_performance_with_large_pdf(self, pdf_extractor, test_pdf_files):
        """Test performance with larger PDF files."""
        # Use one of the existing test files
        test_file = None
        for file_path in test_pdf_files.values():
            if file_path.exists():
                test_file = file_path
                break

        start_time = time.time()

        result = await pdf_extractor.aextract_content(file_path=test_file, name="performance_test")

        end_time = time.time()
        processing_time = end_time - start_time

        assert isinstance(result, list)
        # Ensure processing doesn't take too long (adjust threshold as needed)
        assert processing_time < 60, f"Processing took too long: {processing_time} seconds"

    def test_language_mapping(self, pdf_extractor):
        """Test language code mapping for OCR."""
        assert pdf_extractor._lang_map["en"] == "eng"
        assert pdf_extractor._lang_map["de"] == "deu"

        # Test fallback for unknown language
        unknown_lang = "unknown"
        tesseract_lang = pdf_extractor._lang_map.get(unknown_lang, "eng")
        assert tesseract_lang == "eng"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_extraction(self, pdf_extractor, test_pdf_files):
        """Integration test for complete PDF extraction workflow."""
        for pdf_name, pdf_path in test_pdf_files.items():
            if not pdf_path.exists():
                continue

            result = await pdf_extractor.aextract_content(file_path=pdf_path, name=pdf_name)

            assert isinstance(result, list), f"Result should be a list for {pdf_name}"
            # Analyze results
            text_count = sum(1 for elem in result if elem.type == ContentType.TEXT)
            table_count = sum(1 for elem in result if elem.type == ContentType.TABLE)

            logger.info(f"  Text elements: {text_count}")
            logger.info(f"  Table elements: {table_count}")

            # Verify metadata completeness
            for i, element in enumerate(result):
                assert "document" in element.metadata, f"Missing document in element {i}"
                assert "page" in element.metadata, f"Missing page in element {i}"
                assert "id" in element.metadata, f"Missing id in element {i}"
                assert element.metadata["document"] == pdf_name, f"Wrong document name in element {i}"

            # Verify content is not empty
            non_empty_content = [elem for elem in result if elem.page_content.strip()]
            assert len(non_empty_content) > 0, f"No non-empty content extracted from {pdf_name}"
