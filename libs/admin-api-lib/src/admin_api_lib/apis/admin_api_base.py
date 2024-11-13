# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from admin_api_lib.models.document_status import DocumentStatus
from fastapi import Request, Response, UploadFile


class BaseAdminApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAdminApi.subclasses = BaseAdminApi.subclasses + (cls,)

    async def delete_document(
        self,
        identification: str,
    ) -> None:
        ...

    async def document_reference_id_get(
        self,
        identification: str,
    ) -> Response:
        ...

    async def get_all_documents_status(
        self,
    ) -> list[DocumentStatus]:
        ...

    async def upload_documents_post(
        self,
        body: UploadFile,
        request: Request,
    ) -> None:
        """Uploads user selected pdf documents."""
        ...
