"""Module for the DefaultConfluenceExtractor class."""

import logging
from langchain_community.document_loaders import ConfluenceLoader

from extractor_api_lib.impl.types.extractor_types import ExtractorTypes
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.extractors.information_extractor import InformationExtractor
from extractor_api_lib.impl.mapper.confluence_langchain_document2information_piece import (
    ConfluenceLangchainDocument2InformationPiece,
)
from langchain_community.document_loaders.confluence import ContentFormat


logger = logging.getLogger(__name__)


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
        confluence_loader_parameters = {}
        for key_value in extraction_parameters.kwargs or []:
            if key_value is None or key_value.key is None:
                continue

            value = key_value.value
            if isinstance(value, str):
                value = value.strip()
                if not value and key_value.key in {"space_key", "cql"}:
                    # Skip empty optional parameters
                    continue
                if value.isdigit():
                    value = int(value)

            confluence_loader_parameters[key_value.key] = value

        if "cql" not in confluence_loader_parameters and "space_key" not in confluence_loader_parameters:
            raise ValueError("Either 'space_key' or 'cql' must be provided for Confluence extraction.")
        if (
            "max_pages" in confluence_loader_parameters
            and not confluence_loader_parameters.get("max_pages")
            or isinstance(confluence_loader_parameters.get("max_pages"), str)
        ):
            logging.warning(
                "max_pages parameter is not set or invalid discarding it. ConfluenceLoader will use default value."
            )
            confluence_loader_parameters.pop("max_pages")
        # Drop the document_name parameter as it is not used by the ConfluenceLoader
        if "document_name" in confluence_loader_parameters:
            confluence_loader_parameters.pop("document_name", None)
        confluence_loader_parameters["content_format"] = ContentFormat.VIEW
        document_loader = ConfluenceLoader(**confluence_loader_parameters)
        documents = document_loader.load()
        return [self._mapper.map_document2informationpiece(x, extraction_parameters.document_name) for x in documents]
