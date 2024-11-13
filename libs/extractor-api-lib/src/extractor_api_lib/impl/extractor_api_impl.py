from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
from extractor_api_lib.container import Container
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.models.extraction_request import ExtractionRequest


class ExtractorApiImpl(BaseExtractorApi):
    @inject
    async def extract_information(
        self,
        extraction_request: ExtractionRequest,
        file_extractor: FileExtractor = Depends(Provide[Container.file_extractor]),
    ) -> list[InformationPiece]:
        return await file_extractor.aextract_information(extraction_request)
