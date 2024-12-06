"""Module for the base AdminApi interface."""

# coding: utf-8
# flake8: noqa: D105

from typing import ClassVar, Tuple  # noqa: F401

from admin_api_lib.models.document_status import DocumentStatus
from fastapi import Request, Response, UploadFile


class BaseAdminApi:
    """
    The base AdminApi interface.

    Attributes
    ----------
    subclasses : ClassVar[Tuple]
        A tuple that holds all subclasses of BaseAdminApi.
    """

    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAdminApi.subclasses = BaseAdminApi.subclasses + (cls,)

    async def delete_document(
        self,
        identification: str,
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

    async def document_reference_id_get(
        self,
        identification: str,
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

    async def get_all_documents_status(
        self,
    ) -> list[DocumentStatus]:
        """
        Asynchronously retrieves the status of all documents.

        Returns
        -------
        list[DocumentStatus]
            A list containing the status of all documents.
        """

    async def load_confluence_post(
        self,
    ) -> None:
        """
        Asynchronously loads a Confluence space.

        Returns
        -------
        None
        """

    async def upload_documents_post(
        self,
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
