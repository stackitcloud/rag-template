from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.api_endpoints.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.dependency_container import DependencyContainer


class ExtractorApiImpl(BaseExtractorApi):
    @inject
    async def extract_from_file_post(
        self,
        extraction_request: ExtractionRequest,
        file_extractor: FileExtractor = Depends(Provide[DependencyContainer.file_extractor]),
    ) -> list[InformationPiece]:
        return await file_extractor.aextract_information(extraction_request)

    @inject
    async def extract_from_confluence_post(
        self,
        confluence_parameters: ConfluenceParameters,
        confluence_extractor: ConfluenceExtractor = Depends(Provide[DependencyContainer.confluence_extractor]),
    ) -> list[InformationPiece]:
        return await confluence_extractor.aextract_from_confluence(confluence_parameters)
