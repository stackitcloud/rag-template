"""Module for the DefaultSitemapExtractor class."""

from typing import Optional
from langchain_community.document_loaders import SitemapLoader
import asyncio
import json

from extractor_api_lib.impl.types.extractor_types import ExtractorTypes
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.extractors.information_extractor import InformationExtractor
from extractor_api_lib.impl.mapper.sitemap_document2information_piece import (
    SitemapLangchainDocument2InformationPiece,
)


class SitemapExtractor(InformationExtractor):
    """Implementation of the InformationExtractor interface for confluence."""

    def __init__(
        self,
        mapper: SitemapLangchainDocument2InformationPiece,
        parsing_function: Optional[callable] = None,
        meta_function: Optional[callable] = None,
    ):
        """
        Initialize the SitemapExtractor.

        Parameters
        ----------
        mapper : SitemapLangchainDocument2InformationPiece
            An instance of SitemapLangchainDocument2InformationPiece used for mapping langchain documents
            to information pieces.
        parsing_function : Optional[callable], optional
            A custom parsing function to process the content of the Sitemap, by default None.
        meta_function : Optional[callable], optional
            A custom metadata function to process the metadata of the Sitemap, by default None.
        """
        self._mapper = mapper
        self._parsing_function = parsing_function
        self._meta_function = meta_function

    @property
    def extractor_type(self) -> ExtractorTypes:
        return ExtractorTypes.SITEMAP

    @property
    def mapper(self) -> SitemapLangchainDocument2InformationPiece:
        """Get the mapper instance."""
        return self._mapper

    async def aextract_content(
        self,
        extraction_parameters: ExtractionParameters,
    ) -> list[InternalInformationPiece]:
        """
        Asynchronously extracts information pieces from Sitemap.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
            The parameters required to connect to and extract data from Sitemap.

        Returns
        -------
        list[InternalInformationPiece]
            A list of information pieces extracted from Sitemap.
        """
        sitemap_loader_parameters = self._parse_sitemap_loader_parameters(extraction_parameters)

        if "document_name" in sitemap_loader_parameters:
            sitemap_loader_parameters.pop("document_name", None)

        # Only pass custom functions if they are provided
        if self._parsing_function is not None:
            # Get the actual function from the provider
            sitemap_loader_parameters["parsing_function"] = self._parsing_function
        if self._meta_function is not None:
            # Get the actual function from the provider
            sitemap_loader_parameters["meta_function"] = self._meta_function

        document_loader = SitemapLoader(**sitemap_loader_parameters)
        documents = []
        try:

            def load_documents():
                return list(document_loader.lazy_load())

            documents = await asyncio.get_event_loop().run_in_executor(None, load_documents)
        except Exception as e:
            raise ValueError(f"Failed to load documents from Sitemap: {e}")
        return [self._mapper.map_document2informationpiece(x, extraction_parameters.document_name) for x in documents]

    def _parse_sitemap_loader_parameters(self, extraction_parameters: ExtractionParameters) -> dict:
        """
        Parse the extraction parameters to extract sitemap loader parameters.

        Parameters
        ----------
        extraction_parameters : ExtractionParameters
            The parameters required to connect to and extract data from Sitemap.

        Returns
        -------
        dict
            A dictionary containing the parsed sitemap loader parameters.
        """
        sitemap_loader_parameters = {}
        for x in extraction_parameters.kwargs:
            if x.key == "header_template" or x.key == "requests_kwargs":
                try:
                    sitemap_loader_parameters[x.key] = json.loads(x.value)
                except (json.JSONDecodeError, TypeError):
                    sitemap_loader_parameters[x.key] = x.value if isinstance(x.value, dict) else None
            elif x.key == "filter_urls":
                try:
                    sitemap_loader_parameters[x.key] = json.loads(x.value)
                except (json.JSONDecodeError, TypeError):
                    sitemap_loader_parameters[x.key] = x.value
            else:
                sitemap_loader_parameters[x.key] = int(x.value) if x.value.isdigit() else x.value
        return sitemap_loader_parameters
