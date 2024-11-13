from abc import ABC, abstractmethod

from rag_core_api.models.information_piece import InformationPiece


class InformationPiecesUploader(ABC):
    @abstractmethod
    def upload_information_piece(self, information_piece: list[InformationPiece]):
        pass
