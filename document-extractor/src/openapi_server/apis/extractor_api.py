# coding: utf-8

from typing import List
import importlib
import pkgutil

import openapi_server.impl

from fastapi import APIRouter, Body

from openapi_server.impl.extractor_api_impl import ExtractorApiImpl
from openapi_server.models.extraction_request import ExtractionRequest
from openapi_server.models.information_piece import InformationPiece


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)

implementation = ExtractorApiImpl()


@router.post(
    "/extract",
    responses={
        200: {
            "model": List[InformationPiece],
            "description": "List of extracted information.",
        },
        422: {"description": "Body is not a valid PDF."},
        500: {"description": "Something somewhere went terribly wrong."},
    },
    tags=["extractor"],
    response_model_by_alias=True,
)
async def extract_information(
    extraction_request: ExtractionRequest = Body(None, description=""),
) -> List[InformationPiece]:
    return implementation.extract_information(extraction_request)
