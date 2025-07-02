"""Module for the base ExtractorApi interface."""

# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


class BaseExtractorApi:
    """
    The base ExtractorApi interface.

    Attributes
    ----------
    subclasses : ClassVar[Tuple]
        A tuple containing all subclasses of BaseExtractorApi.
    """

    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseExtractorApi.subclasses = BaseExtractorApi.subclasses + (cls,)

    async def extract_from_file_post(
        self,
        extraction_request: ExtractionRequest,
    ) -> List[InformationPiece]:
        """
        Extract information from a file based on the provided extraction request.

        Parameters
        ----------
        extraction_request : ExtractionRequest
            The request object containing details about the extraction process.

        Returns
        -------
        List[InformationPiece]
            A list of extracted information pieces.
        """

    async def extract_from_source(
        self,
        extraction_parameters: ExtractionParameters,
    ) -> List[InformationPiece]:
        """
        Extract information from a source based on the provided extraction request.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
           The parameters required to access and extract information from the source.

        Returns
        -------
        List[InformationPiece]
            A list of extracted information pieces.
        """
