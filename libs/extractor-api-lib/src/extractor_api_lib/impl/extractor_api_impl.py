"""Module for the implementation of the ExtractorApi interface."""

from fastapi import Depends
from dependency_injector.wiring import Provide, inject

from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.api_endpoints.source_extractor import SourceExtractor
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
from extractor_api_lib.dependency_container import DependencyContainer


class ExtractorApiImpl(BaseExtractorApi):
    """Implementation of the ExtractorApi interface."""

    @inject
    async def extract_from_file_post(
        self,
        extraction_request: ExtractionRequest,
        extractor: FileExtractor = Depends(Provide[DependencyContainer.general_file_extractor]),
    ) -> list[InformationPiece]:
        """
        Extract information from a file based on the provided extraction request.

        Parameters
        ----------
        extraction_request : ExtractionRequest
            The request containing details about the extraction process.
        extractor : FileExtractor, optional
            The file extractor dependency.

        Returns
        -------
        list[InformationPiece]
            A list of extracted information pieces.
        """
        return await extractor.aextract_information(extraction_request)

    async def extract_from_source(
        self,
        extraction_parameters: ExtractionParameters,
        extractor: SourceExtractor = Depends(Provide[DependencyContainer.source_extractor]),
    ) -> list[InformationPiece]:
        """
        Extract information from a source (e.g. confluence) asynchronously.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
            Parameters required to extract information from source.
        extractor : SourceExtractor, optional
            The source extractor instance.

        Returns
        -------
        list[InformationPiece]
            A list of extracted information pieces.
        """
        return await extractor.aextract_information(extraction_parameters)
