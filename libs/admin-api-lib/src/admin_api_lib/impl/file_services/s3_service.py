"""Class to handle I/O with S3 storage."""

import logging
from pathlib import Path
from typing import BinaryIO

import boto3

from admin_api_lib.file_services.file_service import FileService
from admin_api_lib.impl.settings.s3_settings import S3Settings

logger = logging.getLogger(__name__)


class S3Service(FileService):
    """Class to handle I/O with S3 storage."""

    def __init__(self, s3_settings: S3Settings):
        """Class to handle I/O with S3 storage.

        Parameters
        ----------
        s3_settings: S3Settings
            Settings for the s3. Must contain at least the endpoint, access_key_id, secret_access_key and bucket.
        """
        self._s3_settings = s3_settings
        self._s3_client = boto3.client(
            "s3",
            endpoint_url=s3_settings.endpoint,
            aws_access_key_id=s3_settings.access_key_id,
            aws_secret_access_key=s3_settings.secret_access_key,
            aws_session_token=None,
            config=boto3.session.Config(signature_version="s3v4"),
            verify=False,
        )

    def download_folder(self, source: str, target: Path) -> None:
        """Download the remote folder on "source" to the local "target" directory.

        Parameters
        ----------
        source: str
            Path to the remote folder.
        target: Path
            Download destination path.
        """
        target.mkdir(parents=True, exist_ok=True)

        search_response = self._s3_client.list_objects_v2(
            Bucket=self._s3_settings.bucket,
            Prefix=source,
        )
        for found_content in search_response.get("Contents", []):
            file_source = found_content["Key"]
            target_path = target / file_source[len(source) :]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as local_file:
                self.download_file(file_source, local_file)

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
        self._s3_client.download_fileobj(self._s3_settings.bucket, source, target_file)

    def upload_file(self, file_path: str, file_name: str) -> None:
        """
        Upload a local file to the S3 bucket.

        Parameters
        ----------
        source : Path
            The path to the local file to upload.
        target : str
            The target path in the S3 bucket where the file will be stored.
        """
        self._s3_client.upload_file(
            Filename=file_path,
            Bucket=self._s3_settings.bucket,
            Key=file_name,
        )

    def get_all_sorted_file_names(self) -> list[str]:
        """Retrieve all file names stored in the S3 bucket.

        Returns
        -------
        list[str]
            A list of file names stored in the S3 bucket.
        """
        file_names = []

        resp = self._s3_client.list_objects_v2(Bucket=self._s3_settings.bucket)
        if resp.get("Contents"):
            for obj in resp["Contents"]:
                file_names.append(obj["Key"])
        return file_names

    def delete_file(self, file_name: str) -> None:
        """Delete a file from the S3 bucket.

        Parameters
        ----------
        file_name : str
            The name of the file to be deleted from the S3 bucket.
        """
        try:
            file_name = f"/{file_name}" if not file_name.startswith("/") else file_name
            self._s3_client.delete_object(Bucket=self._s3_settings.bucket, Key=file_name)
            logger.info("File %s successfully deleted.", file_name)
        except Exception:
            logger.exception("Error deleting file %s", file_name)
            raise
