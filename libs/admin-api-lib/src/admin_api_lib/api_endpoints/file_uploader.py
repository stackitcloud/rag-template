"""Module for the upload file endpoint."""

from abc import abstractmethod

from fastapi import UploadFile

from admin_api_lib.api_endpoints.uploader_base import UploaderBase


class FileUploader(UploaderBase):
    """File uploader endpoint of the admin API."""

    @abstractmethod
    def cancel_upload(self, identification: str) -> None:
        """
        Signal cancellation for an in-flight upload identified by document id.

        Parameters
        ----------
        identification : str
            Document identification (for example ``file:my_doc.pdf``).
        """

    @abstractmethod
    async def upload_file(
        self,
        base_url: str,
        file: UploadFile,
    ) -> None:
        """
        Upload a source file for content extraction.

        Parameters
        ----------
        base_url : str
            The base url of the service. Is used to determine the download link of the file.
        file : UploadFile
            The file to process.

        Returns
        -------
        None
        """
