"""Comprehensive test suite for SitemapExtractor class."""

from pathlib import Path

import pytest

from extractor_api_lib.impl.extractors.file_extractors.epub_extractor import (
    EpubExtractor,
)
from extractor_api_lib.impl.mapper.langchain_document2information_piece import (
    LangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.content_type import ContentType


class TestEpubExtractor:
    """Test class for EpubExtractor."""

    @pytest.fixture
    def mapper(self) -> LangchainDocument2InformationPiece:
        """Create a LangchainDocument2InformationPiece instance for testing."""
        return LangchainDocument2InformationPiece()

    @pytest.fixture
    def epub_extractor(self, mock_file_service, mapper):
        """Create a EpubExtractor instance for testing."""
        return EpubExtractor(file_service=mock_file_service, mapper=mapper)

    def test_init(self, mock_file_service, mapper):
        """Test EpubExtractor initialization."""
        extractor = EpubExtractor(file_service=mock_file_service, mapper=mapper)
        assert extractor._mapper == mapper
        assert extractor._file_service == mock_file_service

    def test_file_type(self, epub_extractor):
        """Test that extractor_type returns EPUB."""
        assert epub_extractor.compatible_file_types == [FileType.EPUB]

    @pytest.mark.asyncio
    async def test_extract_content_success(self, epub_extractor):
        """Test successful content extraction from an EPUB file."""
        page_content = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam"

        test_data_dir = Path(__file__).parent / "test_data"

        file_path = test_data_dir / "LoremIpsum.epub"
        result = await epub_extractor.aextract_content(file_path, file_path.name)

        assert len(result) == 1
        assert result[0].type == ContentType.TEXT
        assert result[0].page_content == page_content
