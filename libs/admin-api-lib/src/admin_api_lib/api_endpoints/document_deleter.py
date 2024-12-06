"""Module for the document deletion endpoint."""

from abc import ABC, abstractmethod


class DocumentDeleter(ABC):
    """Abstract base class for document deletion endpoint."""

    @abstractmethod
    async def adelete_document(self, identification: str) -> None:
        """
        Delete a document by its identification asynchronously.

        Parameters
        ----------
        identification : str
            The unique identifier of the document to be deleted.

        Returns
        -------
        None
        """
