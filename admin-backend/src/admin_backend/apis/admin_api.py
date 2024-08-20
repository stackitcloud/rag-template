# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from admin_backend.apis.admin_api_base import BaseAdminApi
import admin_backend.impl

from fastapi.responses import StreamingResponse  # noqa: F401
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
    BackgroundTasks,
    UploadFile,
)

from admin_backend.models.extra_models import TokenModel  # noqa: F401


router = APIRouter()

ns_pkg = admin_backend.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/delete_document/{id}",
    responses={
        200: {"description": "Deleted"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def delete_document(
    id: str = Path(..., description=""),
) -> None:
    return BaseAdminApi.subclasses[0]().delete_document(id)


@router.get(
    "/document_reference/{id}",
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
    id: str = Path(..., description="Identifier of the pdf document."),
) -> Response:
    return BaseAdminApi.subclasses[0]().document_reference_id_get(id)


@router.get(
    "/all_documents",
    responses={
        200: {"model": List[str], "description": "List of document links"},
        500: {"description": "Internal server error"},
    },
    tags=["admin"],
    response_model_by_alias=True,
)
async def get_all_documents() -> List[str]:
    return BaseAdminApi.subclasses[0]().get_all_documents()


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
    background_tasks: BackgroundTasks,
) -> None:
    """Uploads user selected pdf documents."""
    return await BaseAdminApi.subclasses[0]().upload_documents_post(body, request, background_tasks)
