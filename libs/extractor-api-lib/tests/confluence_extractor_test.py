"""Tests for the ConfluenceExtractor."""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document as LangchainDocument

from extractor_api_lib.impl.extractors.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.key_value_pair import KeyValuePair
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.impl.types.content_type import ContentType


@pytest.fixture
def confluence_mapper():
    """Return a mapper mock that produces predictable information pieces."""
    mapper = MagicMock()
    mapper.map_document2informationpiece.return_value = InternalInformationPiece(
        type=ContentType.TEXT,
        metadata={"document": "doc", "id": "id", "related": []},
        page_content="content",
    )
    return mapper


@pytest.mark.asyncio
@patch("extractor_api_lib.impl.extractors.confluence_extractor.ConfluenceLoader")
async def test_aextract_content_supports_cql(mock_loader_cls, confluence_mapper):
    """Ensure the extractor forwards the CQL parameter to the loader."""
    extractor = ConfluenceExtractor(mapper=confluence_mapper)
    extraction_parameters = ExtractionParameters(
        document_name="confluence_doc",
        source_type="confluence",
        kwargs=[
            KeyValuePair(key="url", value="https://example.atlassian.net"),
            KeyValuePair(key="token", value="token"),
            KeyValuePair(key="cql", value="type=page"),
        ],
    )

    mock_loader_instance = MagicMock()
    mock_loader_instance.load.return_value = [LangchainDocument(page_content="content", metadata={"title": "Doc"})]
    mock_loader_cls.return_value = mock_loader_instance

    results = await extractor.aextract_content(extraction_parameters)

    assert len(results) == 1
    confluence_mapper.map_document2informationpiece.assert_called_once()
    loader_kwargs = mock_loader_cls.call_args.kwargs
    assert loader_kwargs["cql"] == "type=page"
    assert "space_key" not in loader_kwargs


@pytest.mark.asyncio
async def test_aextract_content_requires_space_key_or_cql(confluence_mapper):
    """The extractor must receive either a space key or a CQL expression."""
    extractor = ConfluenceExtractor(mapper=confluence_mapper)
    extraction_parameters = ExtractionParameters(
        document_name="confluence_doc",
        source_type="confluence",
        kwargs=[
            KeyValuePair(key="url", value="https://example.atlassian.net"),
            KeyValuePair(key="token", value="token"),
        ],
    )

    with pytest.raises(ValueError):
        await extractor.aextract_content(extraction_parameters)
