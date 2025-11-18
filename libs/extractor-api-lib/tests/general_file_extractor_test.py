"""Tests for the GeneralFileExtractor fallback orchestration."""

import pytest
from unittest.mock import MagicMock

from extractor_api_lib.extractors.information_file_extractor import InformationFileExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.api_endpoints.general_file_extractor import GeneralFileExtractor
from extractor_api_lib.impl.types.content_type import ContentType
from extractor_api_lib.impl.types.file_type import FileType
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.extraction_request import ExtractionRequest


class _FailingExtractor(InformationFileExtractor):
    def __init__(self, file_service: FileService, message: str = "failure"):
        super().__init__(file_service)
        self._message = message

    @property
    def compatible_file_types(self) -> list[FileType]:
        return [FileType.PDF]

    async def aextract_content(self, file_path, name):  # pragma: no cover - deterministic failure
        raise RuntimeError(self._message)


class _SuccessfulExtractor(InformationFileExtractor):
    def __init__(self, file_service: FileService, piece: InternalInformationPiece):
        super().__init__(file_service)
        self._piece = piece

    @property
    def compatible_file_types(self) -> list[FileType]:
        return [FileType.PDF]

    async def aextract_content(self, file_path, name):
        return [self._piece]


class _EmptyExtractor(InformationFileExtractor):
    def __init__(self, file_service: FileService):
        super().__init__(file_service)

    @property
    def compatible_file_types(self) -> list[FileType]:
        return [FileType.PDF]

    async def aextract_content(self, file_path, name):
        return []


@pytest.fixture
def file_service():
    """
    Provide a mocked `FileService` that writes placeholder bytes.

    Returns
    -------
    FileService
        MagicMock adhering to the FileService specification.
    """
    service = MagicMock(spec=FileService)

    def _download(_path: str, handle):
        handle.write(b"dummy")

    service.download_file.side_effect = _download
    return service


@pytest.fixture
def mapper():
    """
    Provide a mapper translating internal pieces to their content strings.

    Returns
    -------
    MagicMock
        Mapper mock that echoes the piece content.
    """
    _mapper = MagicMock()
    _mapper.map_internal_to_external.side_effect = lambda piece: piece.page_content
    return _mapper


@pytest.mark.asyncio
async def test_general_file_extractor_fallbacks_to_next_extractor(file_service, mapper):
    """
    Ensure the extractor falls back until one yields content.

    Parameters
    ----------
    file_service : FileService
        Mock file service used to provide temporary files.
    mapper : MagicMock
        Mapper mock that converts internal pieces to strings.
    """
    successful_piece = InternalInformationPiece(
        type=ContentType.TEXT,
        metadata={"document": "doc", "page": 1},
        page_content="content",
    )
    extractors = [
        _FailingExtractor(file_service, message="docling failure"),
        _EmptyExtractor(file_service),
        _SuccessfulExtractor(file_service, successful_piece),
    ]
    general_extractor = GeneralFileExtractor(file_service=file_service, available_extractors=extractors, mapper=mapper)

    request = ExtractionRequest(path_on_s3="s3://bucket/test.pdf", document_name="doc.pdf")
    result = await general_extractor.aextract_information(request)

    assert result == ["content"]
    mapper.map_internal_to_external.assert_called_with(successful_piece)


@pytest.mark.asyncio
async def test_general_file_extractor_raises_when_all_extractors_fail(file_service, mapper):
    """
    Raise a RuntimeError when every extractor fails.

    Parameters
    ----------
    file_service : FileService
        Mock file service used to provide temporary files.
    mapper : MagicMock
        Mapper mock that converts internal pieces to strings.
    """
    extractors = [
        _FailingExtractor(file_service, message="primary failure"),
        _FailingExtractor(file_service, message="secondary failure"),
    ]
    general_extractor = GeneralFileExtractor(file_service=file_service, available_extractors=extractors, mapper=mapper)

    request = ExtractionRequest(path_on_s3="s3://bucket/test.pdf", document_name="doc.pdf")

    with pytest.raises(RuntimeError, match="All extractors failed"):
        await general_extractor.aextract_information(request)
