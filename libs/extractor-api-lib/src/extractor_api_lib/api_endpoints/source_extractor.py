from abc import ABC, abstractmethod

from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.information_piece import InformationPiece


class SourceExtractor(ABC):
    """Abstract base class for extract_from_source endpoint."""

    @abstractmethod
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
