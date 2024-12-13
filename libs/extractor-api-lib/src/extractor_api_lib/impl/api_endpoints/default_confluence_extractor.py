"""Module for the DefaultConfluenceExtractor class."""

from langchain_community.document_loaders import ConfluenceLoader

from extractor_api_lib.api_endpoints.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.impl.mapper.confluence_langchain_document2information_piece import (
    ConfluenceLangchainDocument2InformationPiece,
)
from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.information_piece import InformationPiece


class DefaultConfluenceExtractor(ConfluenceExtractor):
    """Default implementation of the FileExtractor interface."""

    def __init__(
        self,
        mapper: ConfluenceLangchainDocument2InformationPiece,
    ):
        """
        Initialize the DefaultConfluenceExtractor.

        Parameters
        ----------
        mapper : ConfluenceLangchainDocument2InformationPiece
            An instance of ConfluenceLangchainDocument2InformationPiece used for mapping langchain documents
            to information pieces.
        """
        self.mapper = mapper

    async def aextract_from_confluence(self, confluence_parameters: ConfluenceParameters) -> list[InformationPiece]:
        """
        Asynchronously extracts information pieces from Confluence.

        Parameters
        ----------
        confluence_parameters : ConfluenceParameters
            The parameters required to connect to and extract data from Confluence.

        Returns
        -------
        list[InformationPiece]
            A list of information pieces extracted from Confluence.
        """
        self.mapper.confluence_parameters = confluence_parameters
        confluence_loader_parameters = confluence_parameters.model_dump()
        # Drop the document_name parameter as it is not used by the ConfluenceLoader
        confluence_loader_parameters.pop("document_name", None)
        document_loader = ConfluenceLoader(**confluence_loader_parameters)
        documents = document_loader.load()
        return [self.mapper.map_document2informationpiece(x) for x in documents]
