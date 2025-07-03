"""Comprehensive test suite for SitemapExtractor class."""

import asyncio
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.impl.extractors.sitemap_extractor import SitemapExtractor
from extractor_api_lib.impl.types.extractor_types import ExtractorTypes
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.key_value_pair import KeyValuePair
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.impl.types.content_type import ContentType


class TestSitemapExtractor:
    """Test class for SitemapExtractor."""

    @pytest.fixture
    def sitemap_extractor(self, mock_mapper):
        """Create a SitemapExtractor instance for testing."""
        return SitemapExtractor(mapper=mock_mapper)

    @pytest.fixture
    def sample_extraction_parameters(self):
        """Create sample extraction parameters."""
        return ExtractionParameters(
            document_name="test_sitemap_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="filter_urls", value='["https://example.com/page1", "https://example.com/page2"]'),
                KeyValuePair(key="header_template", value='{"User-Agent": "test-agent"}'),
                KeyValuePair(key="max_depth", value="2"),
                KeyValuePair(key="blocksize", value="10"),
            ],
        )

    def test_init(self, mock_mapper):
        """Test SitemapExtractor initialization."""
        extractor = SitemapExtractor(mapper=mock_mapper)
        assert extractor._mapper == mock_mapper

    def test_extractor_type(self, sitemap_extractor):
        """Test that extractor_type returns SITEMAP."""
        assert sitemap_extractor.extractor_type == ExtractorTypes.SITEMAP

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_basic(
        self, mock_sitemap_loader_class, sitemap_extractor, sample_extraction_parameters
    ):
        """Test basic content extraction functionality."""
        # Setup mock SitemapLoader
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance

        # Create mock documents
        mock_documents = [
            LangchainDocument(
                page_content="Content from page 1", metadata={"source": "https://example.com/page1", "title": "Page 1"}
            ),
            LangchainDocument(
                page_content="Content from page 2", metadata={"source": "https://example.com/page2", "title": "Page 2"}
            ),
        ]

        mock_loader_instance.lazy_load.return_value = iter(mock_documents)

        # Setup mock mapper
        expected_info_pieces = [
            InternalInformationPiece(
                type=ContentType.TEXT,
                metadata={"document": "test_sitemap_doc", "id": "id1", "related": []},
                page_content="Content from page 1",
            ),
            InternalInformationPiece(
                type=ContentType.TEXT,
                metadata={"document": "test_sitemap_doc", "id": "id2", "related": []},
                page_content="Content from page 2",
            ),
        ]

        sitemap_extractor.mapper.map_document2informationpiece.side_effect = expected_info_pieces

        # Execute
        result = await sitemap_extractor.aextract_content(sample_extraction_parameters)

        # Verify
        assert len(result) == 2
        assert all(isinstance(piece, InternalInformationPiece) for piece in result)

        # Verify SitemapLoader was called with correct parameters
        mock_sitemap_loader_class.assert_called_once()
        call_args = mock_sitemap_loader_class.call_args[1]

        assert call_args["web_path"] == "https://example.com/sitemap.xml"
        assert call_args["filter_urls"] == ["https://example.com/page1", "https://example.com/page2"]
        assert call_args["header_template"] == {"User-Agent": "test-agent"}
        assert call_args["max_depth"] == 2
        assert call_args["blocksize"] == 10

        # Verify mapper was called for each document
        assert sitemap_extractor.mapper.map_document2informationpiece.call_count == 2

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_json_parsing_failure(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with invalid JSON in parameters falls back to string values."""
        # Create parameters with invalid JSON
        extraction_params = ExtractionParameters(
            document_name="test_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="filter_urls", value="invalid-json["),
                KeyValuePair(key="header_template", value="invalid-json{"),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        result = await sitemap_extractor.aextract_content(extraction_params)

        # Verify
        assert result == []

        # Verify SitemapLoader was called with string fallback values
        call_args = mock_sitemap_loader_class.call_args[1]
        assert call_args["filter_urls"] == "invalid-json["
        assert call_args["header_template"] is None  # Should be None due to invalid JSON

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_header_template_dict_value(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction when header_template is already a dict."""
        extraction_params = ExtractionParameters(
            document_name="test_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="header_template", value={"User-Agent": "direct-dict"}),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        _ = await sitemap_extractor.aextract_content(extraction_params)

        # Verify
        call_args = mock_sitemap_loader_class.call_args[1]
        assert call_args["header_template"] == {"User-Agent": "direct-dict"}

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_document_name_removed(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test that document_name parameter is removed from SitemapLoader parameters."""
        extraction_params = ExtractionParameters(
            document_name="test_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="document_name", value="should_be_removed"),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        await sitemap_extractor.aextract_content(extraction_params)

        # Verify document_name was removed from loader parameters
        call_args = mock_sitemap_loader_class.call_args[1]
        assert "document_name" not in call_args

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_numeric_parameters(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with numeric string parameters."""
        extraction_params = ExtractionParameters(
            document_name="test_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="max_depth", value="5"),
                KeyValuePair(key="blocksize", value="20"),
                KeyValuePair(key="blocknum", value="1"),
                KeyValuePair(key="non_numeric", value="not_a_number"),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        await sitemap_extractor.aextract_content(extraction_params)

        # Verify numeric conversion
        call_args = mock_sitemap_loader_class.call_args[1]
        assert call_args["max_depth"] == 5
        assert call_args["blocksize"] == 20
        assert call_args["blocknum"] == 1
        assert call_args["non_numeric"] == "not_a_number"

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_loader_exception(
        self, mock_sitemap_loader_class, sitemap_extractor, sample_extraction_parameters
    ):
        """Test handling of SitemapLoader exceptions."""
        # Setup mock to raise exception
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.side_effect = Exception("Network error")

        # Execute and verify exception is raised
        with pytest.raises(ValueError, match="Failed to load documents from Sitemap: Network error"):
            await sitemap_extractor.aextract_content(sample_extraction_parameters)

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_empty_documents(
        self, mock_sitemap_loader_class, sitemap_extractor, sample_extraction_parameters
    ):
        """Test extraction when SitemapLoader returns no documents."""
        # Setup mock to return empty list
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        result = await sitemap_extractor.aextract_content(sample_extraction_parameters)

        # Verify
        assert result == []
        sitemap_extractor.mapper.map_document2informationpiece.assert_not_called()

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_minimal_parameters(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with minimal required parameters."""
        extraction_params = ExtractionParameters(
            document_name="minimal_doc",
            source_type="sitemap",
            kwargs=[KeyValuePair(key="web_path", value="https://example.com/sitemap.xml")],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_documents = [LangchainDocument(page_content="Minimal content", metadata={})]
        mock_loader_instance.lazy_load.return_value = iter(mock_documents)

        # Execute
        result = await sitemap_extractor.aextract_content(extraction_params)

        # Verify
        assert len(result) == 1
        mock_sitemap_loader_class.assert_called_once_with(web_path="https://example.com/sitemap.xml")

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_complex_filter_urls(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with complex filter_urls JSON array."""
        extraction_params = ExtractionParameters(
            document_name="complex_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(
                    key="filter_urls", value='[".*\\\\.html$", ".*page[0-9]+.*", "https://example\\\\.com/special/.*"]'
                ),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        await sitemap_extractor.aextract_content(extraction_params)

        # Verify complex JSON parsing
        call_args = mock_sitemap_loader_class.call_args[1]
        expected_patterns = [".*\\.html$", ".*page[0-9]+.*", "https://example\\.com/special/.*"]
        assert call_args["filter_urls"] == expected_patterns

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_no_headers(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction without header_template parameter."""
        extraction_params = ExtractionParameters(
            document_name="no_headers_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="max_depth", value="3"),
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        await sitemap_extractor.aextract_content(extraction_params)

        # Verify no header_template in call args
        call_args = mock_sitemap_loader_class.call_args[1]
        assert "header_template" not in call_args
        assert call_args["max_depth"] == 3

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_with_real_langchain_documents(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with realistic LangChain Document objects."""
        extraction_params = ExtractionParameters(
            document_name="realistic_doc",
            source_type="sitemap",
            kwargs=[KeyValuePair(key="web_path", value="https://example.com/sitemap.xml")],
        )

        # Create realistic documents
        mock_documents = [
            LangchainDocument(
                page_content="""<html><body><h1>Welcome to Example</h1><p>This is the homepage content with useful information about our services.</p></body></html>""",
                metadata={
                    "source": "https://example.com/",
                    "title": "Example Homepage",
                    "loc": "https://example.com/",
                    "lastmod": "2023-12-01",
                    "changefreq": "weekly",
                    "priority": "1.0",
                },
            ),
            LangchainDocument(
                page_content="<html><body><h1>About Us</h1><p>Learn more about our company history and mission.</p></body></html>",
                metadata={
                    "source": "https://example.com/about",
                    "title": "About Us - Example",
                    "loc": "https://example.com/about",
                    "lastmod": "2023-11-15",
                },
            ),
        ]

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter(mock_documents)

        # Execute
        result = await sitemap_extractor.aextract_content(extraction_params)

        # Verify
        assert len(result) == 2
        assert sitemap_extractor.mapper.map_document2informationpiece.call_count == 2

        # Verify mapper was called with correct arguments
        for i, call in enumerate(sitemap_extractor.mapper.map_document2informationpiece.call_args_list):
            args, kwargs = call
            assert args[0] == mock_documents[i]
            assert args[1] == "realistic_doc"

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.asyncio.get_event_loop")
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_executor_usage(
        self, mock_sitemap_loader_class, mock_get_event_loop, sitemap_extractor, sample_extraction_parameters
    ):
        """Test that content extraction uses executor for non-async sitemap loading."""
        # Setup mocks
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop

        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance

        # Create a future that resolves to documents
        mock_documents = [LangchainDocument(page_content="Test content", metadata={})]
        future = asyncio.Future()
        future.set_result(mock_documents)
        mock_loop.run_in_executor.return_value = future

        # Execute
        _ = await sitemap_extractor.aextract_content(sample_extraction_parameters)

        # Verify executor was used
        mock_loop.run_in_executor.assert_called_once()
        executor_call_args = mock_loop.run_in_executor.call_args
        assert executor_call_args[0][0] is None  # First arg should be None (default executor)
        assert callable(executor_call_args[0][1])  # Second arg should be a callable

    def test_extractor_inheritance(self, sitemap_extractor):
        """Test that SitemapExtractor properly inherits from InformationExtractor."""
        from extractor_api_lib.extractors.information_extractor import InformationExtractor

        assert isinstance(sitemap_extractor, InformationExtractor)

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_edge_case_empty_kwargs(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with empty kwargs list."""
        extraction_params = ExtractionParameters(document_name="empty_kwargs_doc", source_type="sitemap", kwargs=[])

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        result = await sitemap_extractor.aextract_content(extraction_params)

        # Verify
        assert result == []
        # Should still call SitemapLoader but with no additional parameters
        mock_sitemap_loader_class.assert_called_once_with()

    @pytest.mark.asyncio
    @patch("extractor_api_lib.impl.extractors.sitemap_extractor.SitemapLoader")
    async def test_aextract_content_mixed_parameter_types(self, mock_sitemap_loader_class, sitemap_extractor):
        """Test extraction with mixed parameter types (strings, numbers, JSON)."""
        extraction_params = ExtractionParameters(
            document_name="mixed_doc",
            source_type="sitemap",
            kwargs=[
                KeyValuePair(key="web_path", value="https://example.com/sitemap.xml"),
                KeyValuePair(key="max_depth", value="3"),  # Will be converted to int
                KeyValuePair(key="continue_on_failure", value="true"),  # Will remain string
                KeyValuePair(key="filter_urls", value='["pattern1", "pattern2"]'),  # Will be parsed as JSON
                KeyValuePair(
                    key="header_template", value='{"Authorization": "Bearer token123"}'
                ),  # Will be parsed as JSON
                KeyValuePair(key="custom_param", value="custom_value"),  # Will remain string
            ],
        )

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_sitemap_loader_class.return_value = mock_loader_instance
        mock_loader_instance.lazy_load.return_value = iter([])

        # Execute
        await sitemap_extractor.aextract_content(extraction_params)

        # Verify parameter processing
        call_args = mock_sitemap_loader_class.call_args[1]
        assert call_args["web_path"] == "https://example.com/sitemap.xml"
        assert call_args["max_depth"] == 3  # Converted to int
        assert call_args["continue_on_failure"] == "true"  # Remained string
        assert call_args["filter_urls"] == ["pattern1", "pattern2"]  # Parsed JSON
        assert call_args["header_template"] == {"Authorization": "Bearer token123"}  # Parsed JSON
        assert call_args["custom_param"] == "custom_value"  # Remained string
