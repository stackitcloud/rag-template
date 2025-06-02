"""Module for the Admin API."""

# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
from typing_extensions import Annotated

import admin_api_lib.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    UploadFile,
    Request,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)
from pydantic import Field, StrictStr


from admin_api_lib.apis.admin_api_base import BaseAdminApi
from admin_api_lib.models.document_status import DocumentStatus
from admin_api_lib.models.http_validation_error import HTTPValidationError
from admin_api_lib.models.key_value_pair import KeyValuePair
from admin_api_lib.models.extra_models import TokenModel  # noqa: F401

router = APIRouter()

ns_pkg = admin_api_lib.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/delete_document/{identification}",
    responses={
        200: {"description": "Deleted"},
        500: {"description": "Internal server error"},
        422: {"model": HTTPValidationError, "description": "Validation Error"},
    },
    tags=["admin"],
    summary="Delete Document",
    response_model_by_alias=True,
)
async def delete_document(
    identification: StrictStr = Path(..., description=""),
) -> None:
    """
    Asynchronously deletes a document based on the provided identification.

    Parameters
    ----------
    identification : str
        The unique identifier of the document to be deleted.

    Returns
    -------
    None
    """
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().delete_document(identification)


@router.get(
    "/document_reference/{identification}",
    responses={
        200: {"model": UploadFile, "description": "Returns the pdf in binary form."},
        400: {"model": str, "description": "Bad request"},
        404: {"model": str, "description": "Document not found."},
        500: {"model": str, "description": "Internal server error"},
        422: {"model": HTTPValidationError, "description": "Validation Error"},
    },
    tags=["admin"],
    summary="Document Reference Id Get",
    response_model_by_alias=True,
)
async def document_reference(
    identification: Annotated[StrictStr, Field(description="Identifier of the document.")] = Path(
        ..., description="Identifier of the document."
    ),
) -> Response:
    """
    Asynchronously retrieve a document reference by its identification.

    Parameters
    ----------
    identification : str
        The unique identifier for the document reference.

    Returns
    -------
    Response
        The response object containing the document reference details.
    """
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().document_reference(identification)


@router.get(
    "/all_documents_status",
    responses={
        200: {"model": List[DocumentStatus], "description": "List of document links"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    summary="Get All Documents Status",
    response_model_by_alias=True,
)
async def get_all_documents_status() -> List[DocumentStatus]:
    """
    Asynchronously retrieves the status of all documents.

    Returns
    -------
    list[DocumentStatus]
        A list containing the status of all documents.
    """
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().get_all_documents_status()


@router.post(
    "/upload_file",
    responses={
        200: {"description": "ok"},
        400: {"description": "Bad request"},
        422: {"description": "Unprocessable Content"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    summary="Upload File",
    response_model_by_alias=True,
)
async def upload_file(
    file: UploadFile,
    request: Request,
) -> None:
    """
    Uploads user selected sources.

    Parameters
    ----------
    file : UploadFile
        The file to be uploaded.
    request : Request
        The HTTP request object containing metadata about the upload request.
    """
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().upload_file(file, request)


@router.post(
    "/upload_source",
    responses={
        200: {"description": "ok"},
        400: {"description": "Bad request"},
        422: {"description": "Unprocessable Content"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    summary="Upload Source",
    response_model_by_alias=True,
)
async def upload_source(
    source_type: StrictStr = Query(None, description="The type of the source"),
    name: StrictStr = Query(None, description="The name of the source", alias="name"),
    key_value_pair: List[KeyValuePair] = Body(None, description="The key-value pairs for the source"),
) -> None:
    """
    Uploads user selected sources.

    Parameters
    ----------
    source_type : str
        The type of the source. Is used by the extractor service to determine the correct extractor to use.
    name : str
        Display name of the source.
    key_value_pair : List[KeyValuePair]
        List of KeyValuePair with parameters used for the extraction.
    """
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().upload_source(source_type, name, key_value_pair)
