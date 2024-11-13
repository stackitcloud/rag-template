from abc import ABC, abstractmethod

from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


class FileExtractor(ABC):
    """Abstract base class for extract_information endpoint."""

    @abstractmethod
    async def aextract_information(self, extraction_request: ExtractionRequest) -> list[InformationPiece]:
        """Extract information of a document, given by the extraction_request."""
        pass
