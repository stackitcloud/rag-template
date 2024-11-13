from pathlib import Path
import tempfile

from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.document_parser.information_extractor import InformationExtractor
from extractor_api_lib.file_services.file_service import FileService
from extractor_api_lib.impl.mapper.internal2external_information_piece import Internal2ExternalInformationPiece
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


class DefaultFileExtractor(FileExtractor):
    """Default implementation of the FileExtractor interface."""

    def __init__(
        self,
        information_extractor: InformationExtractor,
        file_service: FileService,
        mapper: Internal2ExternalInformationPiece,
    ):
        self.information_extractor = information_extractor
        self.file_service = file_service
        self.mapper = mapper

    async def aextract_information(
        self,
        extraction_request: ExtractionRequest,
    ) -> list[InformationPiece]:
        """Extract information of a document, given by the extraction_request."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = Path(temp_dir) / extraction_request.path_on_s3

            with open(temp_file_path, "wb") as temp_file:
                self.file_service.download_file(extraction_request.path_on_s3, temp_file)

            results = self.information_extractor.extract_content(temp_file_path)
            return [self.mapper.map_internal_to_external(x) for x in results if x.page_content is not None]
