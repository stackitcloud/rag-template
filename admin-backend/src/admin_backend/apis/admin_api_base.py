# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from admin_backend.models.document_status import DocumentStatus
from fastapi.responses import StreamingResponse  # noqa: F401
from fastapi import BackgroundTasks, UploadFile, Request, Response


class BaseAdminApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAdminApi.subclasses = BaseAdminApi.subclasses + (cls,)

    async def delete_document(
        self,
        identification: str,
    ) -> None: ...

    async def document_reference_id_get(
        self,
        identification: str,
    ) -> Response: ...

    async def get_all_documents(
        self,
    ) -> List[DocumentStatus]: ...

    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> None:
        """Uploads user selected pdf documents."""
        ...
