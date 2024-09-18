# coding: utf-8

from typing import List, Any, Awaitable  # noqa: F401
import importlib
import pkgutil

from fastapi import Request
from asyncio import CancelledError, wait, create_task, FIRST_COMPLETED, sleep

from rag_core_api.apis.rag_api_base import BaseRagApi
import rag_core_api.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    BackgroundTasks,
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

from rag_core_api.models.extra_models import TokenModel  # noqa: F401
from rag_core_api.models.chat_request import ChatRequest
from rag_core_api.models.chat_response import ChatResponse
from rag_core_api.models.delete_request import DeleteRequest
from rag_core_api.models.search_request import SearchRequest
from rag_core_api.models.search_response import SearchResponse
from rag_core_api.models.upload_source_document import UploadSourceDocument


router = APIRouter()

ns_pkg = rag_core_api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


async def disconnected(request: Request) -> None:
    while True:
        try:
            if await request.is_disconnected():
                break
            await sleep(1.0)
        except CancelledError:
            break


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
    request: Request,
    session_id: str = Path(..., description=""),
    chat_request: ChatRequest = Body(None, description="Chat with RAG."),
) -> ChatResponse | None:
    disconnect_task = create_task(disconnected(request))
    chat_task = create_task(BaseRagApi.subclasses[0]().chat(session_id, chat_request))
    _, pending = await wait(
        [disconnect_task, chat_task],
        return_when=FIRST_COMPLETED,
    )

    # cancel all remaining tasks
    for task in pending:
        task.cancel()
        await task
    if chat_task.done():
        return chat_task.result()
    return None


@router.post(
    "/evaluate",
    responses={
        201: {"description": "Accepted."},
        500: {"description": "Internal Server Error."},
    },
    tags=["rag"],
    response_model_by_alias=True,
)
async def evaluate(
    background_tasks: BackgroundTasks,
) -> None:
    return await BaseRagApi.subclasses[0]().evaluate(background_tasks)


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
    return await BaseRagApi.subclasses[0]().remove_source_documents(delete_request)


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
    return await BaseRagApi.subclasses[0]().search(search_request)


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
    return await BaseRagApi.subclasses[0]().upload_source_documents(upload_source_document)
