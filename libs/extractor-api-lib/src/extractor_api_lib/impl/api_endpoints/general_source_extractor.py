"""Module for the DefaultFileExtractor class."""

import logging

from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.extractors.information_extractor import InformationExtractor
from extractor_api_lib.models.information_piece import InformationPiece
from extractor_api_lib.impl.mapper.internal2external_information_piece import Internal2ExternalInformationPiece
from extractor_api_lib.api_endpoints.source_extractor import SourceExtractor


logger = logging.getLogger(__name__)


class GeneralSourceExtractor(SourceExtractor):
    """A class to extract information from documents using available extractors.

    This class serves as a general extractor that utilizes a list of available
    information extractors to extract content from documents. It determines the
    appropriate extractor based on the file type of the document.
    """

    def __init__(self, available_extractors: list[InformationExtractor], mapper: Internal2ExternalInformationPiece):
        """
        Initialize the GeneralExtractor.

        Parameters
        ----------
        available_extractors : list of InformationExtractor
            A list of available information extractors to be used by the GeneralExtractor.
        mapper : Internal2ExternalInformationPiece
            Mapper for mapping the internal represantation to the external one.
        """
        self._mapper = mapper
        self._available_extractors = available_extractors

    async def aextract_information(
        self,
        extraction_parameters: ExtractionParameters,
    ) -> list[InformationPiece]:
        """
        Extract information from source, using the given parameters.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
            The parameters used to extract information from the source.

        Returns
        -------
        list[InformationPiece]
            A list of extracted information pieces.
        """
        correct_extractors = [
            x for x in self._available_extractors if extraction_parameters.source_type == x.extractor_type
        ]
        if not correct_extractors:
            raise ValueError(f"No extractor found for type {extraction_parameters.source_type}")
        results = await correct_extractors[-1].aextract_content(extraction_parameters)
        return [self._mapper.map_internal_to_external(x) for x in results if x.page_content is not None]
