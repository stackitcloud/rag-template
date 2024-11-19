# coding: utf-8

from typing import List  # noqa: F401
import importlib
import pkgutil

from extractor_api_lib.apis.extractor_api_base import BaseExtractorApi
import extractor_api_lib.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
)

from extractor_api_lib.models.confluence_parameters import ConfluenceParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


router = APIRouter()

ns_pkg = extractor_api_lib.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/extract_from_confluence",
    responses={
        200: {"model": List[InformationPiece], "description": "ok"},
        404: {"description": "not found"},
        422: {"description": "unprocessable entity"},
        500: {"description": "internal server error"},
    },
    tags=["extractor"],
    response_model_by_alias=True,
)
async def extract_from_confluence_post(
    confluence_parameters: ConfluenceParameters = Body(None, description=""),
) -> List[InformationPiece]:
    return await BaseExtractorApi.subclasses[0]().extract_from_confluence_post(confluence_parameters)


@router.post(
    "/extract_from_file",
    responses={
        200: {"model": List[InformationPiece], "description": "List of extracted information."},
        422: {"description": "Body is not a valid PDF."},
        500: {"description": "Something somewhere went terribly wrong."},
    },
    tags=["extractor"],
    response_model_by_alias=True,
)
async def extract_from_file_post(
    extraction_request: ExtractionRequest = Body(None, description=""),
) -> List[InformationPiece]:
    return await BaseExtractorApi.subclasses[0]().extract_from_file_post(extraction_request)
