"""Module for the DefaultConfluenceExtractor class."""

from langchain_community.document_loaders import ConfluenceLoader

from extractor_api_lib.impl.types.extractor_types import ExtractorTypes
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.extractors.information_extractor import InformationExtractor
from extractor_api_lib.impl.mapper.confluence_langchain_document2information_piece import (
    ConfluenceLangchainDocument2InformationPiece,
)


class ConfluenceExtractor(InformationExtractor):
    """Implementation of the InformationExtractor interface for confluence."""

    def __init__(
        self,
        mapper: ConfluenceLangchainDocument2InformationPiece,
    ):
        """
        Initialize the ConfluenceExtractor.

        Parameters
        ----------
        mapper : ConfluenceLangchainDocument2InformationPiece
            An instance of ConfluenceLangchainDocument2InformationPiece used for mapping langchain documents
            to information pieces.
        """
        self._mapper = mapper

    @property
    def extractor_type(self) -> ExtractorTypes:
        return ExtractorTypes.CONFLUENCE

    async def aextract_content(
        self,
        extraction_parameters: ExtractionParameters,
    ) -> list[InternalInformationPiece]:
        """
        Asynchronously extracts information pieces from Confluence.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
            The parameters required to connect to and extract data from Confluence.

        Returns
        -------
        list[InternalInformationPiece]
            A list of information pieces extracted from Confluence.
        """
        # Convert list of key value pairs to dict
        confluence_loader_parameters = {
            x.key: int(x.value) if x.value.isdigit() else x.value for x in extraction_parameters.kwargs
        }
        # Drop the document_name parameter as it is not used by the ConfluenceLoader
        if "document_name" in confluence_loader_parameters:
            confluence_loader_parameters.pop("document_name", None)
        document_loader = ConfluenceLoader(**confluence_loader_parameters)
        documents = document_loader.load()
        return [self._mapper.map_document2informationpiece(x, extraction_parameters.document_name) for x in documents]
