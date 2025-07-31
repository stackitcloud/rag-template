"""Module for the document deletion endpoint."""

from abc import ABC, abstractmethod


class DocumentDeleter(ABC):
    """Abstract base class for document deletion endpoint."""

    @abstractmethod
    async def adelete_document(self, identification: str, remove_from_key_value_store: bool = True) -> None:
        """
        Delete a document by its identification asynchronously.

        Parameters
        ----------
        identification : str
            The unique identifier of the document to be deleted.
        remove_from_key_value_store : bool, optional
            If True, the document will also be removed from the key-value store (default is True).

        Returns
        -------
        None
        """
