from abc import ABC, abstractmethod

from rag_core_api.models.upload_source_document import UploadSourceDocument


class SourceDocumentsUploader(ABC):

    @abstractmethod
    def upload_source_documents(self, source_document: list[UploadSourceDocument]):
        pass
