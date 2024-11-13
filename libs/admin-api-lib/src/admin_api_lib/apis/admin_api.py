# coding: utf-8

import importlib
import pkgutil
from typing import Dict  # noqa: F401

import admin_api_lib.impl
from admin_api_lib.apis.admin_api_base import BaseAdminApi
from admin_api_lib.models.document_status import DocumentStatus
from fastapi import (  # noqa: F401
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    UploadFile,
    status,
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
    return await BaseAdminApi.subclasses[0]().get_all_documents_status()


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
    """Uploads user selected pdf documents."""
    return await BaseAdminApi.subclasses[0]().upload_documents_post(body, request)
