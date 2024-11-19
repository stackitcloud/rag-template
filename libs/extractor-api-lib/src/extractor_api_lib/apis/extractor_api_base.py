# coding: utf-8

from typing import ClassVar, List, Tuple  # noqa: F401

from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


class BaseExtractorApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseExtractorApi.subclasses = BaseExtractorApi.subclasses + (cls,)

    async def extract_from_confluence_post(
        self,
        confluence_parameters: ConfluenceParameters,
    ) -> List[InformationPiece]:
        ...

    async def extract_from_file_post(
        self,
        extraction_request: ExtractionRequest,
    ) -> List[InformationPiece]:
        ...
