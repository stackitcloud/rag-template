"""Module for the InformationPiecesUploader abstract base class."""

from abc import ABC, abstractmethod

from rag_core_api.models.information_piece import InformationPiece


class InformationPiecesUploader(ABC):
    """Abstract base class for uploading information pieces.

    This class defines the interface for uploading a list of information pieces.
    """

    @abstractmethod
    def upload_information_piece(self, information_piece: list[InformationPiece]) -> None:
        """
        Abstract method to upload a list of information pieces.

        Parameters
        ----------
        information_piece : list[InformationPiece]
            A list of InformationPiece objects to be uploaded.

        Returns
        -------
        None
        """
