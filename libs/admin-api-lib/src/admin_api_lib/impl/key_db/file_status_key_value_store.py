"""Module containing the FileStatusKeyValueStore class."""

import json

from redis import Redis

from admin_api_lib.impl.settings.key_value_settings import KeyValueSettings
from admin_api_lib.models.status import Status


class FileStatusKeyValueStore:
    """
    A key-value store for managing file statuses using Redis.

    This class provides methods to upsert, remove, and retrieve file status information
    from a Redis store. Each file status is stored as a JSON string containing the file name
    and its associated status.

    Attributes
    ----------
    STORAGE_KEY : str
        The key under which all file statuses are stored in Redis.
    INNER_FILENAME_KEY : str
        The key used for the file name in the JSON string.
    INNER_STATUS_KEY : str
        The key used for the file status in the JSON string.
    """

    STORAGE_KEY = "stackit-rag-template-files"
    INNER_FILENAME_KEY = "filename"
    INNER_STATUS_KEY = "status"

    def __init__(self, settings: KeyValueSettings):
        """
        Initialize the FileStatusKeyValueStore with the given settings.

        Parameters
        ----------
        settings : KeyValueSettings
            The settings object containing the host and port information for the Redis connection.
        """
        self._redis = Redis(host=settings.host, port=settings.port, decode_responses=True)

    @staticmethod
    def _to_str(file_name: str, file_status: Status) -> str:
        return json.dumps(
            {
                FileStatusKeyValueStore.INNER_FILENAME_KEY: file_name,
                FileStatusKeyValueStore.INNER_STATUS_KEY: file_status,
            }
        )

    @staticmethod
    def _from_str(redis_content: str) -> tuple[str, Status]:
        content_dict = json.loads(redis_content)
        return (
            content_dict[FileStatusKeyValueStore.INNER_FILENAME_KEY],
            content_dict[FileStatusKeyValueStore.INNER_STATUS_KEY],
        )

    def upsert(self, file_name: str, file_status: Status) -> None:
        """
        Upserts the status of a file in the key-value store.

        This method first removes any existing entry for the given file name and then adds the new status.

        Parameters
        ----------
        file_name : str
            The name of the file whose status is to be upserted.
        file_status : Status
            The status to be associated with the file.

        Returns
        -------
        None
        """
        self.remove(file_name)
        self._redis.sadd(self.STORAGE_KEY, FileStatusKeyValueStore._to_str(file_name, file_status))

    def remove(self, file_name: str) -> None:
        """
        Remove the specified file name from the key-value store.

        Parameters
        ----------
        file_name : str
            The name of the file to be removed from the key-value store.

        Returns
        -------
        None
        """
        all_documents = self.get_all()
        correct_file_name = [x for x in all_documents if x[0] == file_name]
        for file_name_related in correct_file_name:
            self._redis.srem(
                self.STORAGE_KEY, FileStatusKeyValueStore._to_str(file_name_related[0], file_name_related[1])
            )

    def get_all(self) -> list[tuple[str, Status]]:
        """
        Retrieve all file status information from the Redis store.

        Returns
        -------
        list[tuple[str, Status]]
            A list of tuples where each tuple contains a string and a Status object.
        """
        all_file_informations = list(self._redis.smembers(self.STORAGE_KEY))
        return [FileStatusKeyValueStore._from_str(x) for x in all_file_informations]
