# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi.responses import StreamingResponse  # noqa: F401
from fastapi import BackgroundTasks, UploadFile, Request, Response


class BaseAdminApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAdminApi.subclasses = BaseAdminApi.subclasses + (cls,)

    def delete_document(
        self,
        id: str,
    ) -> None: ...

    def document_reference_id_get(
        self,
        id: str,
    ) -> Response: ...

    def get_all_documents(
        self,
    ) -> List[str]: ...

    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> None:
        """Uploads user selected pdf documents."""
