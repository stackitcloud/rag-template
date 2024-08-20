# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.extraction_request import ExtractionRequest
from openapi_server.models.information_piece import InformationPiece


class BaseExtractorApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseExtractorApi.subclasses = BaseExtractorApi.subclasses + (cls,)

    def extract_information(
        self,
        extraction_request: ExtractionRequest,
    ) -> List[InformationPiece]: ...
