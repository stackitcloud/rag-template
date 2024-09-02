from pathlib import Path
import tempfile
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from openapi_server.apis.extractor_api_base import BaseExtractorApi
from openapi_server.container import Container
from openapi_server.document_parser.information_extractor import InformationExtractor
from openapi_server.document_parser.information_piece import InformationPiece
from openapi_server.file_services.file_service import FileService
from openapi_server.impl.mapper.internal2external_information_piece import Internal2ExternalInformationPiece
from openapi_server.models.extraction_request import ExtractionRequest


class ExtractorApiImpl(BaseExtractorApi):
    @inject
    def extract_information(
        self,
        extraction_request: ExtractionRequest,
        information_extractor: InformationExtractor = Depends(Provide[Container.general_extractor]),
        file_service: FileService = Depends(Provide[Container.file_service]),
        mapper: Internal2ExternalInformationPiece = Depends(Provide[Container.intern2external]),
    ) -> List[InformationPiece]:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = Path(temp_dir) / extraction_request.path_on_s3
            temp_file = open(temp_file_path, "wb")
            file_service.download_file(extraction_request.path_on_s3, temp_file)
            results = information_extractor.extract_content(temp_file_path)
            return [mapper.map(x) for x in results]
