"""Module for the InformationPieceRemover abstract base class."""

from abc import ABC, abstractmethod

from rag_core_api.models.delete_request import DeleteRequest


class InformationPieceRemover(ABC):
    """Abstract base class for removing information pieces.

    This class defines the interface for removing information pieces based on a given delete request.
    """

    @abstractmethod
    def remove_information_piece(self, delete_request: DeleteRequest) -> None:
        """
        Remove information pieces based on the given delete request.

        Parameters
        ----------
        delete_request : DeleteRequest
            The request object containing the details of the information pieces to be deleted.

        Returns
        -------
        None
        """
