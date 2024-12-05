"""Module for Abstract class for dealing with I/O."""

import abc
from abc import ABC
from pathlib import Path
from typing import BinaryIO


class FileService(ABC):
    """Abstract class for dealing with I/O."""

    @abc.abstractmethod
    def download_folder(self, source: str, target: Path) -> None:
        """Download the remote folder on "source" to the local "target" directory.

        Parameters
        ----------
        source: str
            Path to the remote folder.
        target: Path
            Download destination path.
        """

    @abc.abstractmethod
    def download_file(self, source: str, target_file: BinaryIO) -> None:
        """Read a single remote file "source" into the local "target_file" file-like object.

        Example usage
        =============
        ```
        s3_settings: S3Settings = get_s3_settings()
        s3_service = S3Service(endpoint="endpoint", username="username", password="password", bucket_name="bucket")

        with tempfile.SpooledTemporaryFile(max_size=self._iot_forecast_settings.max_model_size) as temp_file:
            s3_service.download_file("remote_file", temp_file)
            # do stuff with temp_file
        ```

        Parameters
        ----------
        source: str
            Path to the remote folder.
        target_file: BinaryIO
            File-like object to save the data to.
        """

    @abc.abstractmethod
    def upload_file(self, file_path: str, file_name: str) -> None:
        """Upload a local file to the Fileservice.

        Parameters
        ----------
        file_path : str
            The path to the local file to upload.
        file_name : str
            The key in the S3 bucket.
        """

    @abc.abstractmethod
    def get_all_sorted_file_names(self) -> list[str]:
        """Retrieve all file names stored in the file storage.

        Returns
        -------
        list[str]
            A list of file names stored in the file storage.
        """

    @abc.abstractmethod
    def delete_file(self, file_name: str) -> None:
        """Delete a file from the file storage.

        Parameters
        ----------
        file_name : str
            The name of the file to be deleted from the file storage.
        """
