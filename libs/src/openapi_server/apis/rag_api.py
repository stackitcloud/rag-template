# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.rag_api_base import BaseRagApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.models.chat_request import ChatRequest
from openapi_server.models.chat_response import ChatResponse
from openapi_server.models.delete_request import DeleteRequest
from openapi_server.models.search_request import SearchRequest
from openapi_server.models.search_response import SearchResponse
from openapi_server.models.upload_source_document import UploadSourceDocument


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/chat/{session_id}",
    responses={
        200: {"model": ChatResponse, "description": "OK."},
        500: {"description": "Internal Server Error!"},
    },
    tags=["rag"],
    response_model_by_alias=True,
)
async def chat(
    session_id: str = Path(..., description=""),
    chat_request: ChatRequest = Body(None, description="Chat with RAG."),
) -> ChatResponse:
    ...


@router.post(
    "/source_documents/remove",
    responses={
        202: {"description": "Accepted."},
        404: {"description": "Ressource not Found"},
        422: {"description": "ID or metadata missing."},
        500: {"description": "Internal Server Error."},
    },
    tags=["rag"],
    response_model_by_alias=True,
)
async def remove_source_documents(
    delete_request: DeleteRequest = Body(None, description=""),
) -> None:
    ...


@router.post(
    "/search",
    responses={
        200: {"model": SearchResponse, "description": "200."},
        500: {"description": "Internal Server Error."},
    },
    tags=["rag"],
    response_model_by_alias=True,
)
async def search(
    search_request: SearchRequest = Body(None, description=""),
) -> SearchResponse:
    ...


@router.post(
    "/source_documents",
    responses={
        201: {"description": "The file was successful uploaded."},
        422: {"model": str, "description": "Wrong json format."},
        500: {"model": str, "description": "Internal Server Error."},
    },
    tags=["rag"],
    summary="Upload Files for RAG.",
    response_model_by_alias=True,
)
async def upload_source_documents(
    upload_source_document: List[UploadSourceDocument] = Body(None, description=""),
) -> None:
    ...
