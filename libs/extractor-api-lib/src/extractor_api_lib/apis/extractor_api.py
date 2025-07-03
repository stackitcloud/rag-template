"""Module for the Extractor API."""

# coding: utf-8

from typing import Dict, List  # noqa: F401
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
from extractor_api_lib.models.extraction_parameters import ExtractionParameters
from extractor_api_lib.models.extraction_request import ExtractionRequest
from extractor_api_lib.models.information_piece import InformationPiece


router = APIRouter()

ns_pkg = extractor_api_lib.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


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
    """
    Extract information from a file based on the provided extraction request.

    Parameters
    ----------
    extraction_request : ExtractionRequest
        The request object containing details about the extraction process.

    Returns
    -------
    List[InformationPiece]
        A list of extracted information pieces.
    """
    if not BaseExtractorApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseExtractorApi.subclasses[0]().extract_from_file_post(extraction_request)


@router.post(
    "/extract_from_source",
    responses={
        200: {"model": List[InformationPiece], "description": "ok"},
        404: {"description": "not found"},
        422: {"description": "unprocessable entity"},
        500: {"description": "internal server error"},
    },
    tags=["extractor"],
    response_model_by_alias=True,
)
async def extract_from_source(
    extraction_parameters: ExtractionParameters = Body(None, description=""),
) -> List[InformationPiece]:
    """
    Extract information from a source based on the provided extraction parameters.

    Parameters
    ----------
    extraction_parameters : ExtractionParameters, optional
        The request object containing details about the extraction process.

    Returns
    -------
    List[InformationPiece]
        A list of extracted information pieces.

    Raises
    ------
    HTTPException
        If the extraction process fails or encounters an error.
    """
    if not BaseExtractorApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseExtractorApi.subclasses[0]().extract_from_source(extraction_parameters)
