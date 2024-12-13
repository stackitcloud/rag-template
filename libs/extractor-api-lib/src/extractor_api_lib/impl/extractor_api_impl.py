"""Module for the implementation of the ExtractorApi interface."""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from extractor_api_lib.api_endpoints.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.api_endpoints.file_extractor import FileExtractor
from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
from extractor_api_lib.dependency_container import DependencyContainer
from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


class ExtractorApiImpl(BaseExtractorApi):
    """Implementation of the ExtractorApi interface."""

    @inject
    async def extract_from_file_post(
        self,
        extraction_request: ExtractionRequest,
        file_extractor: FileExtractor = Depends(Provide[DependencyContainer.file_extractor]),
    ) -> list[InformationPiece]:
        """
        Extract information from a file based on the provided extraction request.

        Parameters
        ----------
        extraction_request : ExtractionRequest
            The request containing details about the extraction process.
        file_extractor : FileExtractor, optional
            The file extractor dependency, by default Depends(Provide[DependencyContainer.file_extractor]).

        Returns
        -------
        list[InformationPiece]
            A list of extracted information pieces.
        """
        return await file_extractor.aextract_information(extraction_request)

    @inject
    async def extract_from_confluence_post(
        self,
        confluence_parameters: ConfluenceParameters,
        confluence_extractor: ConfluenceExtractor = Depends(Provide[DependencyContainer.confluence_extractor]),
    ) -> list[InformationPiece]:
        """
        Extract information from Confluence asynchronously.

        Parameters
        ----------
        confluence_parameters : ConfluenceParameters
            Parameters required to extract information from Confluence.
        confluence_extractor : ConfluenceExtractor, optional
            The Confluence extractor instance (default is provided by DependencyContainer).

        Returns
        -------
        list[InformationPiece]
            A list of extracted information pieces from the configured Confluence space.
        """
        return await confluence_extractor.aextract_from_confluence(confluence_parameters)
