"""Module for the DefaultSitemapExtractor class."""

from typing import Optional
from langchain_community.document_loaders import SitemapLoader
import asyncio
import json
import logging

from extractor_api_lib.impl.types.extractor_types import ExtractorTypes
from extractor_api_lib.models.dataclasses.internal_information_piece import InternalInformationPiece
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.extractors.information_extractor import InformationExtractor
from extractor_api_lib.impl.mapper.sitemap_document2information_piece import (
    SitemapLangchainDocument2InformationPiece,
)
from extractor_api_lib.impl.utils.sitemap_extractor_utils import (
    astro_sitemap_metadata_parser_function,
    astro_sitemap_parser_function,
    docusaurus_sitemap_metadata_parser_function,
    docusaurus_sitemap_parser_function,
    generic_sitemap_metadata_parser_function,
    generic_sitemap_parser_function,
)

logger = logging.getLogger(__name__)


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
        """Get the type of the extractor."""
        return ExtractorTypes.SITEMAP

    @property
    def mapper(self) -> SitemapLangchainDocument2InformationPiece:
        """Get the mapper instance."""
        return self._mapper

    @staticmethod
    def _select_parser_functions(
        parser_override: Optional[str],
    ) -> tuple[Optional[callable], Optional[callable]]:
        mapping = {
            "docusaurus": (docusaurus_sitemap_parser_function, docusaurus_sitemap_metadata_parser_function),
            "astro": (astro_sitemap_parser_function, astro_sitemap_metadata_parser_function),
            "generic": (generic_sitemap_parser_function, generic_sitemap_metadata_parser_function),
        }

        if not parser_override:
            return None, None

        normalized = str(parser_override).strip().lower()

        if normalized not in mapping:
            logger.warning("Unknown sitemap_parser '%s'. Falling back to generic.", parser_override)
            normalized = "generic"

        return mapping[normalized]

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
        sitemap_loader_parameters, parser_override = self._parse_sitemap_loader_parameters(extraction_parameters)

        if "document_name" in sitemap_loader_parameters:
            sitemap_loader_parameters.pop("document_name", None)

        parsing_function = self._parsing_function
        meta_function = self._meta_function

        override_parsing_function, override_meta_function = self._select_parser_functions(parser_override)
        if override_parsing_function is not None:
            parsing_function = override_parsing_function
        if override_meta_function is not None:
            meta_function = override_meta_function

        if parsing_function is not None:
            sitemap_loader_parameters["parsing_function"] = parsing_function
        if meta_function is not None:
            sitemap_loader_parameters["meta_function"] = meta_function

        if "continue_on_failure" not in sitemap_loader_parameters:
            sitemap_loader_parameters["continue_on_failure"] = True

        document_loader = SitemapLoader(**sitemap_loader_parameters)
        documents = []
        try:

            def load_documents():
                return list(document_loader.lazy_load())

            documents = await asyncio.get_event_loop().run_in_executor(None, load_documents)
        except Exception as e:
            raise ValueError(f"Failed to load documents from Sitemap: {e}")
        return [self._mapper.map_document2informationpiece(x, extraction_parameters.document_name) for x in documents]

    def _parse_sitemap_loader_parameters(
        self, extraction_parameters: ExtractionParameters
    ) -> tuple[dict, Optional[str]]:
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
        parser_override: Optional[str] = None
        for x in extraction_parameters.kwargs or []:
            if x.key in ("sitemap_parser", "parser"):
                parser_override = str(x.value) if x.value is not None else None
                continue
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
            elif x.key == "continue_on_failure":
                if isinstance(x.value, bool):
                    sitemap_loader_parameters[x.key] = x.value
                elif isinstance(x.value, str):
                    normalized = x.value.strip().lower()
                    if normalized in ("true", "1", "yes", "y", "on"):
                        sitemap_loader_parameters[x.key] = True
                    elif normalized in ("false", "0", "no", "n", "off"):
                        sitemap_loader_parameters[x.key] = False
                    else:
                        sitemap_loader_parameters[x.key] = x.value
                else:
                    sitemap_loader_parameters[x.key] = x.value
            else:
                sitemap_loader_parameters[x.key] = int(x.value) if x.value.isdigit() else x.value
        return sitemap_loader_parameters, parser_override
