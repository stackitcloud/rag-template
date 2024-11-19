from extractor_api_lib.api_endpoints.confluence_extractor import ConfluenceExtractor
from extractor_api_lib.impl.mapper.confluence_langchain_document2information_piece import (
    ConfluenceLangchainDocument2InformationPiece,
)
from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.information_piece import InformationPiece
from langchain_community.document_loaders import ConfluenceLoader


class DefaultConfluenceExtractor(ConfluenceExtractor):
    """Default implementation of the FileExtractor interface."""

    def __init__(
        self,
        mapper: ConfluenceLangchainDocument2InformationPiece,
    ):
        self.mapper = mapper

    async def aextract_from_confluence(self, confluence_parameters: ConfluenceParameters) -> list[InformationPiece]:
        self.mapper.confluence_parameters = confluence_parameters
        confluence_loader_parameters = confluence_parameters.model_dump()
        document_loader = ConfluenceLoader(**confluence_loader_parameters)
        documents = document_loader.load()
        return [self.mapper.map_document2informationpiece(x) for x in documents]
