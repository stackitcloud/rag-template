import json
from typing import Tuple
from redis import Redis

from admin_backend.impl.settings.key_value_settings import KeyValueSettings
from admin_backend.models.status import Status


class FileStatusKeyValueStore:
    STORAGE_KEY = "files"
    INNER_FILENAME_KEY = "filename"
    INNER_STATUS_KEY = "status"

    def __init__(self, settings: KeyValueSettings):
        self._redis = Redis(host=settings.host, port=settings.port, decode_responses=True)

    def upsert(self, file_name: str, file_status: Status) -> None:
        self.remove(file_name)
        self._redis.sadd(self.STORAGE_KEY, FileStatusKeyValueStore._to_str(file_name, file_status))

    def remove(self, file_name: str) -> None:
        all_documents = self.get_all()
        correct_file_name = [x for x in all_documents if x[0] == file_name]
        for file_name_related in correct_file_name:
            self._redis.srem(
                self.STORAGE_KEY, FileStatusKeyValueStore._to_str(file_name_related[0], file_name_related[1])
            )

    def get_all(self) -> list[Tuple[str, Status]]:
        all_file_informations = list(self._redis.smembers(self.STORAGE_KEY))
        return [FileStatusKeyValueStore._from_str(x) for x in all_file_informations]

    @staticmethod
    def _to_str(file_name: str, file_status: Status) -> str:
        return json.dumps(
            {
                FileStatusKeyValueStore.INNER_FILENAME_KEY: file_name,
                FileStatusKeyValueStore.INNER_STATUS_KEY: file_status,
            }
        )

    @staticmethod
    def _from_str(redis_content: str) -> Tuple[str, Status]:
        content_dict = json.loads(redis_content)
        return (
            content_dict[FileStatusKeyValueStore.INNER_FILENAME_KEY],
            content_dict[FileStatusKeyValueStore.INNER_STATUS_KEY],
        )
