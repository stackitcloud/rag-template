"""Module for the Chunker abstract base class."""

from abc import ABC, abstractmethod

from langchain_core.documents import Document


class Chunker(ABC):
    """Abstract base class for chunking documents into smaller parts."""

    @abstractmethod
    def chunk(self, documents: Document) -> list[Document]:
        """
        Chunk the given documents into smaller parts.

        Parameters
        ----------
        documents : Document
            The documents to be chunked.

        Returns
        -------
        list of Document
            A list of smaller parts obtained by chunking the documents.
        """
