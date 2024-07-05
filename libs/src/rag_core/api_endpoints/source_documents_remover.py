from abc import ABC, abstractmethod

from rag_core.models.delete_request import DeleteRequest


class SourceDocumentsRemover(ABC):

    @abstractmethod
    def remove_source_documents(self, delete_request: DeleteRequest) -> None:
        pass
