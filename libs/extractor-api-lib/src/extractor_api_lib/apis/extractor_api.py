# coding: utf-8

import importlib
import pkgutil

from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
import extractor_api_lib.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from extractor_api_lib.models.extra_models import TokenModel  # noqa: F401
from typing import List
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


router = APIRouter()

ns_pkg = extractor_api_lib.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/extract",
    responses={
        200: {"model": list[InformationPiece], "description": "list of extracted information."},
        422: {"description": "Body is not a valid PDF."},
        500: {"description": "Something somewhere went terribly wrong."},
    },
    tags=["extractor"],
    response_model_by_alias=True,
)
async def extract_information(
    extraction_request: ExtractionRequest = Body(None, description=""),
) -> List[InformationPiece]:
    return await BaseExtractorApi.subclasses[0]().extract_information(extraction_request)
