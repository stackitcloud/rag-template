import pytest
from unittest.mock import MagicMock

from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.impl.mapper.sitemap_document2information_piece import (
    SitemapLangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.types.content_type import ContentType


@pytest.fixture
def mock_mapper():
    """Create a mock mapper for testing."""
    mapper = MagicMock(spec=SitemapLangchainDocument2InformationPiece)
    mapper.map_document2informationpiece.return_value = InternalInformationPiece(
        type=ContentType.TEXT,
        metadata={"document": "test_doc", "id": "test_id", "related": []},
        page_content="Test content",
    )
    return mapper
