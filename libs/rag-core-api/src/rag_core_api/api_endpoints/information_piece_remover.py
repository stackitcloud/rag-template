from abc import ABC, abstractmethod

from rag_core_api.models.delete_request import DeleteRequest


class InformationPieceRemover(ABC):
    @abstractmethod
    def remove_information_piece(self, delete_request: DeleteRequest) -> None:
        pass
