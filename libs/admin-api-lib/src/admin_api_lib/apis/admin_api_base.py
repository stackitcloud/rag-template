"""Module for the base AdminApi interface."""

# coding: utf-8
# flake8: noqa: D105

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from typing_extensions import Annotated

from pydantic import Field, StrictStr
from fastapi import Request, Response, UploadFile

from admin_api_lib.models.document_status import DocumentStatus
from admin_api_lib.models.key_value_pair import KeyValuePair


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
        identification: StrictStr,
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

    async def document_reference(
        self,
        identification: Annotated[StrictStr, Field(description="Identifier of the document.")],
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

    async def upload_source(
        self,
        source_type: StrictStr,
        name: StrictStr,
        key_value_pair: List[KeyValuePair],
    ) -> None:
        """
        Asynchronously uploads user selected source.

        Parameters
        ----------
        source_type : str
            The type of the source. Is used by the extractor service to determine the correct extractor to use.
        name : str
            Display name of the source.
        key_value_pair : list[KeyValuePair]
            List of KeyValuePair with parameters used for the extraction.

        Returns
        -------
        None
        """

    async def upload_file(
        self,
        file: UploadFile,
        request: Request,
    ) -> None:
        """
        Asynchronously uploads user-selected documents.

        Parameters
        ----------
        file : UploadFile
            The file object containing the source documents to be uploaded.
        request : Request
            The request object containing metadata about the upload request.

        Returns
        -------
        None
        """
