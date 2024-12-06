"""Module for the Admin API."""

# coding: utf-8

import importlib
import pkgutil

import admin_api_lib.impl
from admin_api_lib.apis.admin_api_base import BaseAdminApi
from admin_api_lib.models.document_status import DocumentStatus
from fastapi import (  # noqa: F401
    APIRouter,
    Path,
    Request,
    Response,
    UploadFile,
)


router = APIRouter()

ns_pkg = admin_api_lib.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/delete_document/{identification}",
    responses={
        200: {"description": "Deleted"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def delete_document(
    identification: str = Path(..., description=""),
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
    return await BaseAdminApi.subclasses[0]().delete_document(identification)


@router.get(
    "/document_reference/{identification}",
    responses={
        200: {"model": UploadFile, "description": "Returns the pdf in binary form."},
        400: {"model": str, "description": "Bad request"},
        404: {"model": str, "description": "Document not found."},
        500: {"model": str, "description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def document_reference_id_get(
    identification: str = Path(..., description="Identifier of the pdf document."),
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
    return await BaseAdminApi.subclasses[0]().document_reference_id_get(identification)


@router.get(
    "/all_documents_status",
    responses={
        200: {"model": list[DocumentStatus], "description": "list of document links"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def get_all_documents_status() -> list[DocumentStatus]:
    """
    Asynchronously retrieves the status of all documents.

    Returns
    -------
    list[DocumentStatus]
        A list containing the status of all documents.
    """
    return await BaseAdminApi.subclasses[0]().get_all_documents_status()


@router.post(
    "/load_confluence",
    responses={
        200: {"description": "Loading from confluence is successful"},
        423: {
            "description": (
                "if the confluence loader is already processing a request,"
                "no further requests are possible. The user needs to wait,"
                "till the preliminary request finished processing."
            )
        },
        500: {"description": "Internal Server Error"},
        501: {"description": "The confluence loader is not set up"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def load_confluence_post() -> None:
    """
    Asynchronously loads a Confluence space.

    Returns
    -------
    None
    """
    return await BaseAdminApi.subclasses[0]().load_confluence_post()


@router.post(
    "/upload_documents",
    responses={
        200: {"description": "ok"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def upload_documents_post(
    body: UploadFile,
    request: Request,
) -> None:
    """
    Asynchronously uploads user-selected source documents.

    Parameters
    ----------
    body : UploadFile
        The file object containing the source documents to be uploaded.
    request : Request
        The request object containing metadata about the upload request.

    Returns
    -------
    None
    """
    return await BaseAdminApi.subclasses[0]().upload_documents_post(body, request)
